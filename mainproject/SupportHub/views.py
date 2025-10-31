from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile,Complaint,ComplaintReport, Notification
from django.contrib.auth import authenticate, login, logout
from django.http import FileResponse, Http404
from django.contrib.auth import update_session_auth_hash

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        profile_picture = request.FILES.get('profile_picture')  # ✅ new
        first_name = request.POST.get('first_name')

        # Basic validation
        if not username or not email or not password:
            messages.error(request, "Please fill all required fields.")
            return redirect('register')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        # ✅ Create User only once
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.save()

        # ✅ Create linked UserProfile
        UserProfile.objects.create(
            user=user,
            phone=phone,
            address=address,
            profile_picture=profile_picture  # store uploaded image
        )

        messages.success(request, "Account created successfully! You can now log in.")
        return redirect('login')

    return render(request, 'Register.html')

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # ✅ works fine, because our view name isn’t "login"
            messages.success(request, "Login successful!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def dashboard(request):
    """
    Dashboard for logged-in users.
    Displays stats and user's complaints summary.
    """
    user = request.user

    # Get user's complaints
    user_complaints = Complaint.objects.filter(user=user).order_by('-created_at')

    # Calculate stats
    total_complaints = user_complaints.count()
    pending_complaints = user_complaints.filter(status='Pending').count()
    resolved_complaints = user_complaints.filter(status='Resolved').count()
    inprogress_complaints = user_complaints.filter(status='In Progress').count()
    closed_complaints = user_complaints.filter(status='Closed').count()

    context = {
        'user_complaints': user_complaints,
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'resolved_complaints': resolved_complaints,
        'inprogress_complaints': inprogress_complaints,
        'closed_complaints': closed_complaints,
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
def dashboard(request):
    user = request.user

    user_complaints = Complaint.objects.filter(user=user).order_by('-created_at')
    total_complaints = user_complaints.count()
    pending_complaints = user_complaints.filter(status='Pending').count()
    resolved_complaints = user_complaints.filter(status='Resolved').count()

    # Notifications
    new_notifications = Notification.objects.filter(user=user, is_read=False)
    notification_count = new_notifications.count()

    context = {
        'user_complaints': user_complaints,
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'resolved_complaints': resolved_complaints,
        'notification_count': notification_count,
        'new_notifications': new_notifications,
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='login')
def register_complaints(request):
    """
    View for users to register new complaints.
    """
    user = request.user

    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        description = request.POST.get('description')

        # Validate
        if not title or not category or not description:
            messages.error(request, "Please fill in all required fields.")
            return redirect('register_complaints')

        # Save complaint
        Complaint.objects.create(
            user=user,
            title=title,
            category=category,
            description=description
        )

        messages.success(request, "Complaint submitted successfully!")
        return redirect('dashboard')

    return render(request, 'complaints.html')

@login_required(login_url='login')
def submit_complaint(request):
    """
    View for submitting a new complaint.
    The complaint will automatically appear in the Django admin dashboard.
    """
    user = request.user

    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        description = request.POST.get('description')

        # Validate fields
        if not title or not category or not description:
            messages.error(request, "Please fill in all required fields.")
            return redirect('submit_complaint')

        # Create and save the complaint
        Complaint.objects.create(
            user=user,
            title=title,
            category=category,
            description=description,
            status='Pending'  # default status
        )

        messages.success(request, "Complaint submitted successfully!")
        return redirect('dashboard')  # after submission, redirect to dashboard

    return render(request, 'complaints.html')

@login_required(login_url='login')
def pending_complaints(request):
    """
    Show only the user's pending complaints.
    """
    complaints = Complaint.objects.filter(user=request.user, status='Pending').order_by('-created_at')
    return render(request, 'complaints_list.html', {
        'complaints': complaints,
        'page_title': 'Pending Complaints'
    })

@login_required(login_url='login')
def resolved_complaints(request):
    """
    Show only the user's resolved complaints.
    """
    complaints = Complaint.objects.filter(user=request.user, status='Resolved').order_by('-created_at')
    return render(request, 'complaints_list.html', {
        'complaints': complaints,
        'page_title': 'Resolved Complaints'
    })

@login_required
def user_reports(request):
    """
    Show all complaint reports belonging to the logged-in user.
    """
    reports = ComplaintReport.objects.filter(complaint__user=request.user)
    return render(request, 'user_reports.html', {'reports': reports})

@login_required
def download_report(request, report_id):
    """
    Allow user to download their report file.
    """
    report = get_object_or_404(ComplaintReport, id=report_id, complaint__user=request.user)

    if not report.attached_file:
        raise Http404("Report file not found.")

    # Return the file as a downloadable response
    response = FileResponse(report.attached_file.open('rb'), as_attachment=True, filename=report.filename)
    return response

@login_required
def view_report(request, report_id):
    report = get_object_or_404(
        ComplaintReport, 
        id=report_id, 
        complaint__user=request.user
    )
    return render(request, 'view_report.html', {'report': report})

@login_required(login_url='login')
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Mark all as read when opened
    notifications.update(is_read=True)
    return render(request, 'notifications.html', {'notifications': notifications})

@login_required
def track_complaints(request):
    complaints = Complaint.objects.filter(user=request.user)
    return render(request, 'track_complaints.html', {'complaints': complaints})

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .models import UserProfile

@login_required
def user_settings(request):
    user = request.user
    # Ensure user profile exists
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Update user fields
        name = request.POST.get('name')
        email = request.POST.get('email')

        if name:
            user.first_name = name
        if email:
            user.email = email
        user.save()

        # Update profile fields
        profile.phone = request.POST.get('phone', profile.phone)
        profile.address = request.POST.get('address', profile.address)

        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        profile.save()

        # Update password if provided
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if current_password and new_password and confirm_password:
            if not user.check_password(current_password):
                messages.error(request, "Current password is incorrect.")
            elif new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # keep logged in

        messages.success(request, "Profile updated successfully.")
        return redirect('dashboard')  # 🔹 redirect to dashboard

    context = {'user': user, 'profile': profile}
    return render(request, 'settings.html', context)




def logout_view(request):
    logout(request)
    return redirect('Home')  # Change 'home' to your actual home page name

