from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
#from django.contrib.auth.models import User , auth
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, OrderForm


from django.contrib.auth.models import User  # Django user model for session management
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, OrderForm
from .dynamo_db_utils import authenticate_dynamodb_user

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('place_order')
    else:
        form = LoginForm()
    return render(request, 'orders/login.html', {'form': form})

@login_required
def place_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            return redirect('order_success')
    else:
        form = OrderForm()
    return render(request, 'orders/place_order.html', {'form': form})

def order_success(request):
    return render(request, 'orders/order_success.html')



def track_home(request):
    # if request.method == 'POST':
    #     form = LoginForm(request, data=request.POST)
    #     if form.is_valid():
    #         username = form.cleaned_data.get('username')
    #         password = form.cleaned_data.get('password')
    #         user = authenticate(request, username=username, password=password)
    #         if user is not None:
    #             login(request, user)
    #             return render(request, 'orders/track_home.html')
    # else:
    #     form = LoginForm()
    # return redirect('/')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Use custom DynamoDB authentication function
            user_data = authenticate_dynamodb_user(username, password)
            if user_data:
                # Create a temporary Django User for session handling
                django_user, _ = User.objects.get_or_create(username=username)
                login(request, django_user)  # Log the user in
                return render(request, 'orders/track_home.html')
            else:
                # Authentication failed, add error message
                form.add_error(None, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'orders/user_login.html', {'form': form})

def ship_now(request):
    return render(request, 'orders/ship_now.html')

def user_login(request):
    
    return render(request, 'orders/user_login.html')
