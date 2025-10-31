from django.db import models
from django.contrib.auth.models import User



class UserProfile(models.Model):
    """
    Extends Django's built-in User to store extra information (optional)
    for users who register complaints.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Complaint(models.Model):
    """
    Complaint model for users to submit complaints.
    Admin (superuser) can update status and remarks.
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    CATEGORY_CHOICES = [
        ('IT', 'IT Issue'),
        ('HR', 'HR Issue'),
        ('Maintenance', 'Maintenance'),
        ('Finance', 'Finance'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    admin_remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.user.username}) - {self.status}"
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    complaint = models.ForeignKey("Complaint", on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"



class ComplaintReport(models.Model):
    """
    A report file that admin uploads once a complaint is resolved.
    """
    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE, related_name='report')
    report_title = models.CharField(max_length=200)
    report_content = models.TextField(blank=True, null=True)
    attached_file = models.FileField(upload_to='reports/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.complaint.title}"

    @property
    def filename(self):
        """Get just the filename for display."""
        return self.attached_file.name.split('/')[-1] if self.attached_file else None

