from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout

# Signup view
def signup(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['pass1']
        confirm_password = request.POST['pass2']

        if password != confirm_password:
            messages.warning(request, "Passwords do not match")
            return render(request, 'signup.html')

        try:
            if User.objects.get(username=email):
                messages.info(request, "Email is already registered")
                return render(request, 'signup.html')
        except User.DoesNotExist:
            pass

        # Create the user
        user = User.objects.create_user(username=email, email=email, password=password)
        user.save()

        messages.success(request, "Signup successful! Please log in.")
        return redirect('/auth/login/')

    return render(request, "signup.html")


# Login view
def handlelogin(request):
    if request.method == "POST":
        username = request.POST['email']
        userpassword = request.POST['pass1']
        myuser = authenticate(username=username, password=userpassword)

        if myuser is not None:
            login(request, myuser)
            messages.success(request, "Login successful")
            return redirect('/')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('/auth/login')

    return render(request, 'login.html')


# Logout view
def handlelogout(request):
    logout(request)
    messages.info(request,"Log Out Success")

    return redirect("/auth/login")
