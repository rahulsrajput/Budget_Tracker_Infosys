from django.contrib import admin
from .models import Income , Expense, Budget , Category, EMI, Report, User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
class UserAdmin(BaseUserAdmin):

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["username","name", "email", "phone", "is_admin"]  # Fields shown in the user list view
    list_filter = ["is_admin"]  # Adds a filter sidebar in the list view for 'is_admin'
    
    # Fieldsets define the layout of fields in the admin form for the user.
    fieldsets = [
        (None, {"fields": ["email", "password","username"]}),  # Display email and password at the top
        ("Personal info", {"fields": ["name", "phone"]}),  # Group name and phone under 'Personal info'
        ("Permissions", {"fields": ["is_admin"]}),  # Display admin permission control
    ]
    
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a new user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],  # Apply the 'wide' class to the fields for styling
                "fields": ["email", "phone", "password1", "password2"],  # Fields for creating a new user
            },
        ),
    ]
    
    # Search functionality in the admin panel. This enables searching by email.
    search_fields = ["email"]
    
    # Ordering of the list view results by email in ascending order.
    ordering = ["email"]
    
    # No need for additional horizontal filters in this case
    filter_horizontal = []


# Register the User model and the customized UserAdmin
admin.site.register(User, UserAdmin)


admin.site.register(Category)
admin.site.register(Income)
admin.site.register(Expense)
admin.site.register(Budget)
admin.site.register(EMI)
admin.site.register(Report)