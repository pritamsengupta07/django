# Import necessary modules
import email
import html
import os
import random
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
import openai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import LoginData
from .models import Chat

from django.utils import timezone
from django.contrib.auth.models import AnonymousUser



# from .serializers import MoreInfo_Serial, User_Serial


os.environ["OPENAI_API_KEY"] = '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'
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_openai(request, message):
    try:
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None  # or any other value that represents an unauthenticated state
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": message}],
            max_tokens=150,
            temperature=0.7,
        )
        
        answer = response['choices'][0]['message']['content'].strip()
        Chat.objects.create(user=user, message=message, response=response)
        return answer
    except openai.error.OpenAIError as e:
        return f"Error from OpenAI API: {e}"
def chatbot(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(request, message)  # Pass both request and message to the function

        return JsonResponse({'message': message, 'response': response})
    
    return render(request, "chat.html")

# # Global variables
otp = ""
username = ""
otp_timestamp = None

# Function to generate OTP
def generate_otp():
    global otp, otp_timestamp
    otp_code = "".join([str(random.randint(0, 9)) for _ in range(6)])
    otp_timestamp = datetime.now()
    return otp_code

# Function to validate OTP
def validate_otp(user_input, otpl):
    global otp_timestamp
    time_limit = timedelta(minutes=1, seconds=30)
    
    if datetime.now() > otp_timestamp + time_limit:
        return False

    return user_input == otpl

# View to redirect to the homepage
def index(request):
    return render(request, "base.html")






# View for user login
def login_user(request):
    if request.method == "POST":
        un = request.POST.get("username")
        pw = request.POST.get("password")
        # group = request.POST.get("group")

        if un and pw:
            user = authenticate(request, username=un, password=pw)

            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                LoginData.objects.create(username=un, success=True)
                return redirect('index')  # Redirect to the desired page after successful login
                
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please provide both username and password.')

    return render(request, "login.html")
# View to log out the user
def logout_user(request):
    logout(request)
    return redirect('index')

# View for user registration
def registration_user(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")
        password1 = request.POST.get("password1")

        if password != password1:
            messages.error(request, "Passwords do not match.")
            return redirect("registration")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("registration")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("registration")

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        # Generate and send OTP via email
        global otp
        otp = generate_otp()
        print(otp)
        subject = "OTP CODE"
        message = f"Your OTP is: {otp}"
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.email]  # Update with the recipient email
        try:
            send_mail(
                subject,
                message,
                email_from,
                recipient_list,
                fail_silently=False,
            )
            print("Email sent successfully.")

            if send_mail:
                return redirect("otp")
        except Exception as e:
            print(f"An error occurred: {e}")
            return redirect("registration")

        messages.success(request, 'Registration successful! You can now log in.')
        return redirect("login")

    return render(request, "registration.html")

def otp_code(request):
    if request.method == "POST":
        uiotp = request.POST.get("otp")
        global otp
        print(f"user:{uiotp}")
        print(f"in:{otp}")
        user_input = uiotp
        if validate_otp(user_input, otp):
            return redirect("index")
        else:
            return redirect("registration")

    return render(request, "otp.html")

