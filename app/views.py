from django.forms import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, decorators
from .models import Category, Income, Expense, Budget, EMI
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth import get_user_model
import json

# Create your views here.
User = get_user_model()


@decorators.login_required(login_url='login')
def home_view(request):
    income = Income.objects.filter(user=request.user)
    
    expense_obj = Expense.objects.filter(user=request.user).order_by('-date')[:4]    

    budgets = request.user.budgets.all().order_by('-amount_limit')[:2]

    emis = request.user.emis.all().order_by('-amount')[:2]

    data = {
        "income": float(request.user.total_income()),
        "expense": float(request.user.total_expense()),
        "emi": float(request.user.total_emi()),
        "budget": float(request.user.total_budget()),
    }


    return render(request, 'home.html', context={'expense_obj':expense_obj, 'income':income,  'budgets':budgets, 'emis':emis, 'data':json.dumps(data)})



# Auth
def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = authenticate(request, email=email, password=password)
        login(request, user_obj)
        return redirect('home')  # Redirect to your desired page after login
    return render(request, 'login.html')


def register_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        username = request.POST.get('username')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validate that passwords match
        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('register')  # Redirect back to the registration page

        # Validate password strength
        if len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters long")
            return redirect('register')

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use")
            return redirect('register')

        # Create new user
        try:
            user = User.objects.create_user(username=username, email=email, name=name, phone=phone, password=password1)
            user.save()
            login(request, user)
            return redirect('home')
        except ValidationError as e:
            messages.error(request, f"Error: {e}")
            return redirect('register')

    else:
        return render(request, 'register.html')
    

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('login')
    else:
        return redirect('login')
    



# Category
def category_add(request):
    category_types = Category.CATEGORY_TYPES
    if request.method == "POST":
        name = request.POST.get("name")
        category_type = request.POST.get("category")
        Category.objects.create(user=request.user, name=name, category_type=category_type).save()
        return redirect('expense-add')
    return render(request, 'category_add.html',context={'category_types':category_types})






# Expense
@decorators.login_required(login_url='login')
def expenses_view(request):     
    expense_obj = Expense.objects.filter(user=request.user).order_by('-date')
    total_expenses = expense_obj.aggregate(Sum('amount'))['amount__sum'] 
    
    # Filter :
    expense_categories = request.user.categories.filter(category_type='Expense')
    
    
    return render(request, 'expenses.html', context={'expense_obj':expense_obj, 'total_expenses':total_expenses, 'expense_categories':expense_categories})


@decorators.login_required(login_url='login')
def expense_add_view(request):
    if request.method == "POST":
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        date = request.POST.get('date')
        is_fixed = 'is_fixed' in request.POST
        # Retrieve the selected category from the database
        category = Category.objects.get(id=category_id)
        # Save the new expense record
        expense = Expense.objects.create(user=request.user ,amount=amount, description=description, category=category, date=date, is_fixed=is_fixed)
        expense.save()
        return redirect('home')
    expense_categories = request.user.categories.filter(category_type='Expense')
    return render(request, 'expense_add.html', context={'expense_categories':expense_categories})


@decorators.login_required(login_url='login')
def expense_update_view(request, id):
    expense = get_object_or_404(Expense, user=request.user, id=id)
    
    expense_categories = request.user.categories.filter(category_type='Expense')
    
    if request.method == 'POST':
        # Process form submission
        amount = request.POST.get('amount')
        category_id = request.POST.get('category')
        description = request.POST.get('description', '').strip()
        date = request.POST.get('date')
        is_fixed = 'is_fixed' in request.POST  # Checkbox value
        
        # Validate and save
        try:
            expense.amount = amount
            expense.category = get_object_or_404(Category, id=category_id, user=request.user)
            expense.description = description
            expense.date = date
            expense.is_fixed = is_fixed
            expense.save()
            return redirect('expenses')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return render(request, 'expense_update.html', context={'expense':expense, 'expense_categories':expense_categories})


@decorators.login_required(login_url='login')
def expense_delete_view(request, id):
    expense_id = get_object_or_404(Expense, user=request.user, id=id)
    expense_id.delete()
    return redirect('home')
    







# Income
@decorators.login_required(login_url='login')
def income_add_view(request):
    if request.method == "POST":
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('date')
        category_id = request.POST.get('category')
        category = Category.objects.get(id=category_id)

        # Save the new income record
        income = Income.objects.create(user=request.user, amount=amount, description=description, date=date, category=category)
        income.save()
        return redirect('home')
    income_categories = request.user.categories.filter(category_type='Income')
    return render(request, 'income_add.html', context={'income_categories':income_categories})



@decorators.login_required(login_url='login')
def income_update_view(request, id):
    income = get_object_or_404(Income, user=request.user, id=id)
    if request.method == "POST":
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('date')
        category_id = request.POST.get('category')
        category = Category.objects.get(id=category_id)
        # Save the new income record
        try:
            income.amount = amount
            income.description = description
            income.date = date
            income.category = category
            income.save()
            return redirect('home')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    income_categories = request.user.categories.filter(category_type='Income')
    return render(request, 'income_update.html', context={'income':income,'income_categories':income_categories})



@decorators.login_required(login_url='login')
def income_delete_view(request, id):
    income = get_object_or_404(Income, user=request.user, id=id)
    income.delete()
    return redirect('home')













# Budget
def budgets_view(request):
    budgets = request.user.budgets.all()
    return render(request, 'budgets.html', context={'budgets':budgets})


def budget_add_view(request):
    expense_categories = request.user.categories.filter(category_type='Expense')
    if request.method == "POST":
        amount_limit = request.POST.get('amount_limit')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        category_id = request.POST.get('category')
        category = Category.objects.get(id=category_id)
        budget = Budget.objects.create(user=request.user, amount_limit=amount_limit, start_date=start_date, end_date=end_date, category=category)
        budget.save()
        return redirect('home')
    return render(request, 'budget_add.html', context={'expense_categories':expense_categories})



def budget_update_view(request, id):
    budget = get_object_or_404(Budget, user=request.user, id=id)
    expense_categories = request.user.categories.filter(category_type='Expense')
    
    if request.method == "POST":
        amount_limit = request.POST.get('amount_limit')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        category_id = request.POST.get('category')
        category = Category.objects.get(id=category_id)

        try:
            budget.amount_limit = amount_limit
            budget.start_date = start_date
            budget.end_date = end_date
            budget.category = category
            budget.save()
            return redirect('budgets')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return render(request, 'budget_update.html', context={'budget':budget, 'expense_categories':expense_categories})


def budget_delete_view(request, id):
    budget = get_object_or_404(Budget, user=request.user, id=id)
    budget.delete()
    return redirect('home')





# EMI
def emi_view(request):
    emis = request.user.emis.all()
    return render(request, 'emi.html',context={'emis':emis})


def emi_add_view(request):
    if request.method == "POST":
        amount = request.POST.get('amount')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        next_payment_date = request.POST.get('next_payment_date')
        description = request.POST.get('description')
        frequency = request.POST.get('frequency')
        emi = EMI.objects.create(user=request.user, amount=amount, next_payment_date=next_payment_date, start_date=start_date, end_date=end_date, description=description, frequency=frequency)
        emi.save()
        return redirect('home')
    return render(request, 'emi_add.html',context={})



def emi_update_view(request, id):
    emi = get_object_or_404(EMI, user=request.user, id=id)
    
    if request.method == "POST":
        amount = request.POST.get('amount')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        next_payment_date = request.POST.get('next_payment_date')
        description = request.POST.get('description')
        frequency = request.POST.get('frequency')

        try:
            emi.amount = amount
            emi.start_date = start_date
            emi.end_date = end_date
            emi.next_payment_date = next_payment_date
            emi.frequency = frequency
            emi.description = description
            emi.save()
            return redirect('emi')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return render(request, 'emi_update.html',context={'emi':emi})



def emi_delete_view(request, id):
    emi = get_object_or_404(EMI, user=request.user, id=id)
    emi.delete()
    return redirect('home')




# Report Generate
def generate_report(request):
    return render(request, 'generate_report.html', context={})