from django.contrib import admin
from .models import Complaint, UserProfile, Notification, ComplaintReport


# ✅ Inline admin for ComplaintReport (NOT registered as admin)
class ComplaintReportInline(admin.StackedInline):
    model = ComplaintReport
    extra = 0  # allows adding one report at a time
    fields = ('report_title', 'report_content', 'attached_file')
    readonly_fields = ('created_at',)


# ✅ Complaint admin with inline
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'created_at')
    inlines = [ComplaintReportInline]

    def save_model(self, request, obj, form, change):
        # Check if complaint was changed to 'Resolved'
        if change:
            old_obj = Complaint.objects.get(pk=obj.pk)
            if old_obj.status != 'Resolved' and obj.status == 'Resolved':
                # Create notification
                Notification.objects.create(
                    user=obj.user,
                    complaint=obj,
                    message=f"Your complaint '{obj.title}' has been resolved."
                )
        super().save_model(request, obj, form, change)


# ✅ User profile admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address', 'created_at')


# ✅ Complaint report admin (separate, simple registration)
@admin.register(ComplaintReport)
class ComplaintReportAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'report_title', 'created_at')
    search_fields = ('report_title', 'complaint__title')




    