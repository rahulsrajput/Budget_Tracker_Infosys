from django.db import models
from django.contrib.auth.models import User, AbstractBaseUser, PermissionsMixin
from django.conf import settings
from .managers import UserManager


# Create your models here.

class User(AbstractBaseUser, PermissionsMixin):
    # Custom User model inheriting AbstractBaseUser (authentication) and PermissionsMixin (permissions)

    # Email field with validation and uniqueness
    email = models.EmailField(
        verbose_name="email address",  # Human-readable name for email
        max_length=255,  # Maximum length for the email field
        unique=True,  # Ensures email is unique
    )

    username = models.CharField(max_length=50, unique=True, blank=True, null=True)  # Optional username field


    # User's full name with a max length of 50 characters
    name = models.CharField(max_length=50)

    # User's phone number, stored as a string (max length 10)
    phone = models.CharField(max_length=10)

    # Flag to indicate whether the user account is active
    is_active = models.BooleanField(default=True)  # Defaults to active

    # Flag to determine if the user is an admin (for staff permissions)
    is_admin = models.BooleanField(default=False)

    # Custom manager for user creation
    objects = UserManager()

    # The field to use for user identification (email in this case)
    USERNAME_FIELD = "email"

    # Fields required for creating a user (besides the email)
    REQUIRED_FIELDS = ["name", "phone", "username"]

    def __str__(self):
        return self.email  # Display the email as the string representation of the user

    def has_perm(self, perm, obj=None):
        """Check if the user has a specific permission (simplified here to always return True)."""
        return True

    def has_module_perms(self, app_label):
        """Check if the user has permission to view the specified app (simplified to always return True)."""
        return True

    @property
    def is_staff(self):
        """Return True if the user is an admin (used by Django to determine if the user is staff)."""
        return self.is_admin

    def total_income(self):
        """Calculate the total income for the user."""
        return sum(income.amount for income in self.income.all()) if self.income.exists() else 0

    def total_expense(self):
        """Calculate the total expenses for the user."""
        return sum(expense.amount for expense in self.expenses.all()) if self.expenses.exists() else 0

    def total_savings(self):
        """Calculate the user's total savings (income - expenses)."""
        return self.total_income() - self.total_expense() if self.income.exists() and self.expenses.exists() else self.total_income()

    def total_budget(self):
        return sum(budget.amount_limit for budget in self.budgets.all()) if self.budgets.exists() else 0

    def total_emi(self):
        return sum(emi.amount for emi in self.emis.all()) if self.emis.exists() else 0


class Category(models.Model):
    # Define a Django model named 'Category', which creates a database table for categories.

    INCOME = 'Income'  # Constant for the "Income" category type.
    EXPENSE = 'Expense'  # Constant for the "Expense" category type.

    CATEGORY_TYPES = [  # A list of choices for the 'category_type' field.
        (INCOME, 'Income'),  # First choice is "Income".
        (EXPENSE, 'Expense'),  # Second choice is "Expense".
    ]

    user = models.ForeignKey(  # Foreign key to associate categories with a user.
        User,  # Refers to the User model.
        on_delete=models.CASCADE,  # Deletes categories when the user is deleted.
        blank=True,  # Allows this field to be left empty.
        null=True,  # Allows this field to store NULL values.
        related_name='categories'  # Allows reverse querying using 'categories' on the User model.
    )

    name = models.CharField(  # Field for the category name.
        max_length=50,  # Maximum length of the name is 50 characters.
    )

    category_type = models.CharField(  # Field for the type of category (Income or Expense).
        max_length=10,  # Maximum length of the category type is 10 characters.
        choices=CATEGORY_TYPES  # Limits the field to predefined choices (Income/Expense).
    )

    created_at = models.DateTimeField(  # Field to store when the category was created.
        auto_now_add=True  # Automatically sets the current timestamp when created.
    )

    def __str__(self):  # String representation of the category object.
        return f"{self.name} ({self.category_type})"  # Displays the category name and type in admin or shell.






class Income(models.Model):
    # Define a Django model named 'Income', which represents income records for users.

    user = models.ForeignKey(  # Foreign key to associate income records with a user.
        User,  # Refers to the User model.
        on_delete=models.CASCADE,  # Deletes income records if the associated user is deleted.
        related_name='income'  # Allows reverse querying using 'income' on the User model.
    )

    amount = models.DecimalField(  # Field to store the income amount.
        max_digits=10,  # Maximum number of digits in the amount (including decimal places).
        decimal_places=2  # Number of digits after the decimal point (e.g., 12345.67).
    )

    category = models.ForeignKey(  # Foreign key to associate the income with a category.
        Category,  # Refers to the Category model.
        on_delete=models.CASCADE,  # Deletes income records if the associated category is deleted.
        limit_choices_to={'category_type': 'Income'},  # Limits category choices to "Income" type.
        related_name='income'  # Allows reverse querying using 'income' on the Category model.
    )

    description = models.TextField(  # Field to store an optional description for the income.
        blank=True,  # Allows this field to be left empty in forms.
        null=True  # Allows this field to store NULL values in the database.
    )

    date = models.DateField()  # Field to store the date of the income.

    created_at = models.DateTimeField(  # Field to store when the income record was created.
        auto_now_add=True  # Automatically sets the current timestamp when created.
    )

    def __str__(self):  # String representation of the income object.
        return f"{self.user.username} - {self.category.name} - {self.amount}"  
        # Displays the username, category name, and amount in admin or shell.




class Expense(models.Model):
    # Define a Django model named 'Expense', which represents expense records for users.

    user = models.ForeignKey(  # Foreign key to associate expense records with a user.
        User,  # Refers to the User model.
        on_delete=models.CASCADE,  # Deletes expense records if the associated user is deleted.
        related_name='expenses'  # Allows reverse querying using 'expenses' on the User model.
    )

    amount = models.DecimalField(  # Field to store the expense amount.
        max_digits=10,  # Maximum number of digits in the amount (including decimal places).
        decimal_places=2  # Number of digits after the decimal point (e.g., 12345.67).
    )

    category = models.ForeignKey(  # Foreign key to associate the expense with a category.
        Category,  # Refers to the Category model.
        on_delete=models.CASCADE,  # Deletes expense records if the associated category is deleted.
        limit_choices_to={'category_type': 'Expense'},  # Limits category choices to "Expense" type.
        related_name='expenses'  # Allows reverse querying using 'expenses' on the Category model.
    )

    description = models.TextField(  # Field to store an optional description for the expense.
        blank=True,  # Allows this field to be left empty in forms.
        null=True  # Allows this field to store NULL values in the database.
    )

    date = models.DateField()  # Field to store the date of the expense.

    is_fixed = models.BooleanField(  # Field to indicate if the expense is fixed (e.g., rent, subscription).
        default=False  # Default value is False, meaning the expense is not fixed.
    )

    created_at = models.DateTimeField(  # Field to store when the expense record was created.
        auto_now_add=True  # Automatically sets the current timestamp when created.
    )

    def __str__(self):  # String representation of the expense object.
        return f"{self.user.username} - {self.category.name} - {self.amount}"  
        # Displays the username, category name, and amount in admin or shell.








class Budget(models.Model):
    # Define a Django model named 'Budget', which represents a budget record for users.

    user = models.ForeignKey(  # Foreign key to associate the budget with a user.
        User,  # Refers to the User model.
        on_delete=models.CASCADE,  # Deletes the budget record if the associated user is deleted.
        related_name='budgets'  # Allows reverse querying using 'budgets' on the User model.
    )

    category = models.ForeignKey(  # Foreign key to associate the budget with a category.
        Category,  # Refers to the Category model.
        on_delete=models.CASCADE  # Deletes the budget record if the associated category is deleted.
    )

    amount_limit = models.DecimalField(  # Field to store the budget limit amount.
        max_digits=10,  # Maximum number of digits in the amount (including decimal places).
        decimal_places=2  # Number of digits after the decimal point (e.g., 1000.00).
    )

    start_date = models.DateField()  # Field to store the start date of the budget period.

    end_date = models.DateField()  # Field to store the end date of the budget period.

    def __str__(self):  # String representation of the budget object.
        return f"{self.user.username} - {self.category.name} Budget {self.amount_limit}"  
        # Displays the username, category name, and the budget amount in admin or shell.






class Alert(models.Model):
    # Define a Django model named 'Alert', which represents notifications or alerts for users.

    user = models.ForeignKey(  # Foreign key to associate alerts with a user.
        User,  # Refers to the User model.
        on_delete=models.CASCADE,  # Deletes alerts if the associated user is deleted.
        related_name='alerts'  # Allows reverse querying using 'alerts' on the User model.
    )

    message = models.TextField()  # Field to store the alert message content.

    is_read = models.BooleanField(  # Field to indicate if the alert has been read by the user.
        default=False  # Default value is False, meaning the alert is unread.
    )

    created_at = models.DateTimeField(  # Field to store when the alert was created.
        auto_now_add=True  # Automatically sets the current timestamp when created.
    )

    def __str__(self):  # String representation of the alert object.
        return f"Alert for {self.user.username}: {self.message[:30]}"  
        # Displays the username and the first 30 characters of the alert message in admin or shell.







class Report(models.Model):
    # Define a Django model named 'Report', which represents reports generated for users.

    user = models.ForeignKey(  # Foreign key to associate reports with a user.
        User,  # Refers to the User model.
        on_delete=models.CASCADE,  # Deletes reports if the associated user is deleted.
        related_name='reports'  # Allows reverse querying using 'reports' on the User model.
    )

    report_type = models.CharField(  # Field to specify the type of the report.
        max_length=50  # Maximum length of the report type is 50 characters.
    )

    start_date = models.DateField()  # Field to store the start date for the report.

    end_date = models.DateField()  # Field to store the end date for the report.

    file_path = models.FileField(  # Field to store the file path of the generated report.
        upload_to='reports/',  # Specifies the folder where uploaded files will be saved.
        blank=True,  # Allows this field to be left empty in forms.
        null=True  # Allows this field to store NULL values in the database.
    )

    created_at = models.DateTimeField(  # Field to store when the report was created.
        auto_now_add=True  # Automatically sets the current timestamp when created.
    )

    def __str__(self):  # String representation of the report object.
        return f"Report for {self.user.username} - {self.report_type}"  
        # Displays the username and the type of report in admin or shell.






class EMI(models.Model):
    # Define a Django model named 'EMI', which represents Equated Monthly Installments for users.

    user = models.ForeignKey(  # Foreign key to associate EMIs with a user.
        User,  # Refers to the User model.
        on_delete=models.CASCADE,  # Deletes EMI records if the associated user is deleted.
        related_name='emis'  # Allows reverse querying using 'emis' on the User model.
    )

    amount = models.DecimalField(  # Field to store the EMI amount.
        max_digits=10,  # Maximum number of digits in the amount (including decimal places).
        decimal_places=2  # Number of digits after the decimal point (e.g., 12345.67).
    )

    start_date = models.DateField()  # Field to store the start date of the EMI.

    end_date = models.DateField()  # Field to store the end date of the EMI.

    frequency = models.CharField(  # Field to specify the frequency of EMI payments.
        max_length=20  # Maximum length of the frequency string (e.g., "Monthly").
    )

    description = models.TextField(  # Field to store an optional description of the EMI.
        blank=True,  # Allows this field to be left empty in forms.
        null=True  # Allows this field to store NULL values in the database.
    )

    next_payment_date = models.DateField()  # Field to store the date of the next EMI payment.

    def __str__(self):  # String representation of the EMI object.
        return f"{self.user.username} - EMI {self.amount} - {self.frequency}"  
        # Displays the username, EMI amount, and payment frequency in admin or shell.
