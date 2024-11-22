from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

#from django.contrib.auth.models import User , auth
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from .sns import *
from .lambda_utils import *

from django.contrib.auth.models import User  # Django user model for session management
#from django.contrib.auth.decorators import login_required
from .forms import LoginForm, OrderForm
from .dynamo_db_utils import *
import logging,json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def order_success(request):
    return render(request, 'orders/order_success.html')


def track_home(request):
    username = request.session.get('username', 'User')
    return render(request, 'orders/track_home.html', {'username': username})


# def login_required(function):
#     """
#     Decorator to ensure the user is logged in.
#     """
#     def wrapper(request, *args, **kwargs):
#         if 'username' not in request.session:
#             return redirect('login_view')  # Redirect to login page if not logged in
#         return function(request, *args, **kwargs)
#     return wrapper

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form :
            username = request.POST.get('username')
            password = request.POST.get('password')

            # Use custom DynamoDB authentication function
            user_data = authenticate_dynamodb_user(username, password)
            if user_data is not None:
                request.session['username'] = username
                return redirect('track_home')
            else:
                # Authentication failed, add error message
                #form.add_error(None, "Invalid username or password.")
                return render(request, 'orders/user_login.html', {'form': form})
    else:
        # form = LoginForm()
        #return redirect('user_login')
        return render(request, 'orders/user_login.html')

def signup_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form :
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email')
            add_user('Users', username, email, password, 'us-east-1')
            topic_arn = create_sns_topic(username)
            subscribe_to_topic(topic_arn, 'email', email)
            return render(request, 'orders/user_login.html')
    else:
        # form = LoginForm()
        #return redirect('user_login')
        return render(request, 'orders/user_login.html')


@csrf_exempt
def ship_now(request):
    logger.info("\n\nUser placed1 order")
  #  form = OrderForm(request, data=request.POST)
    success_message = None
    if request.method == 'POST':
        values_json = request.POST.get('values')
        values_data = json.loads(values_json)
        pickup_location = values_data.get('pickup_location')
        drop_location = values_data.get('drop_location')
        username = request.session.get('username', 'User')
        logger.info("\n\nUser placed order {}".format(pickup_location))
        email = get_email_from_dynamodb(username)
        logger.info("\n\nemail {}".format(email))
        topic_arn = get_topic_by_name(username)
        values_data['username'] = username
        values_data['topic_arn'] = topic_arn
        #send_order_confirmation_email_via_sns(username, pickup_location, drop_location, topic_arn)
        logger.info("\n\n\nSending email via lambda {} \n\n\n\n {}".format(values_data,values_json))
        invoke_lambda(json.dumps(values_data))
        save_order_to_dynamodb(username, pickup_location, drop_location)
        success_message = "Order placed successfully!"
        logger.info("\n\nUser placed order {}".format(success_message))
        #return render(request, 'orders/ship_now.html', {'success_message': success_message})
    
    return render(request, 'orders/ship_now.html', {'success_message': success_message})
    #, {'success_message': success_message})
    # else:
    #     logger.info("\n\nUser placed2 order") 
    #     return render(request, 'orders/ship_now.html')

   
def order_list(request):
    username = request.session.get('username', 'User')
    user_orders = get_user_orders(username)
    return render(request, 'orders/order_list.html', {'orders': user_orders})

       

def user_login(request):
    return render(request, 'orders/user_login.html')
    
def delete(request,index):
    logger.info("\n\nDelete requested")
    if request.method == "POST" and 'delete' in request.POST:
        logger.info("\n\nUser deleted order")
        username = request.session.get('username', 'User')
        # values_json = request.POST.get('values')
        # values_data = json.loads(values_json)
        remove_element_from_db(username,index-1)
    return redirect('order_list')



def place_order(request):
    success_message = None
    if request.method == 'POST':
        # Process the form data
        logger.info("\n\norder details: {} ".format(request))
        logger.info("POST data: %s", request.POST)
        logger.info("\n\nUser placed3 order")
        values_json = request.POST.get('values')
        values_data = json.loads(values_json)
        pickup_location = values_data.get('pickup_location')
        drop_location = values_data.get('drop_location')
        #username = request.user.username  # Get the logged-in user's username
        username = request.session.get('username', 'User')
        logger.info("\n\nUser placed order {}".format(pickup_location))
        email = get_email_from_dynamodb(username)
        logger.info("\n\nemail {}".format(email))
        
        #publish_message(get_topic_by_name('order_notify'), "This is a test message.", subject="Test Subject")
        save_order_to_dynamodb(username, pickup_location, drop_location)
        
        
        # Add success message
        # messages.success(request, "Order placed successfully!")
        success_message = "Order placed successfully!"
        logger.info("\n\nUser placed order {}".format(success_message))  # Render the form page 
    return render(request, 'orders/order_success.html', {'success_message': success_message}) 
    
def logout_view(request):
    """
    Logs out the user by clearing the session data.
    """
    request.session.flush()  # Clears all session data for the user
    return redirect('login_view')  # Redirect to the login page or any other page    