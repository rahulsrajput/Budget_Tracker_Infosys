from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    """Custom manager for creating users and superusers"""

    def create_user(self, name, email, phone, username, password=None):
        """Create and return a regular user with an email, phone, name, and password"""
        
        # Ensure that the user provides an email address
        if not email:
            raise ValueError("Users must have an email address")
        
        # Create a new user instance
        user = self.model(
            email=self.normalize_email(email),  # Normalize the email to lowercase
            phone=phone,
            name=name,
            username=username
        )
        
        # Set the password securely
        user.set_password(password)
        
        # Save the user to the database
        user.save(using=self._db)
        
        return user

    def create_superuser(self, name, email, username, phone, password=None):
        """Create and return a superuser with admin privileges"""
        
        # Create a regular user first
        user = self.create_user(
            name=name,
            email=email,
            phone=phone,
            password=password,
            username=username,
        )
        
        # Set the user as an admin
        user.is_admin = True
        
        # Save the superuser to the database
        user.save(using=self._db)
        
        return user
