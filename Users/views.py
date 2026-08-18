from django.shortcuts import render,redirect
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import registerForm,loginForm

# Create your views here.
# def index(request):
#     return render(request,'Users/index.html')

def register(request):
    if request.method == 'POST':
        form = registerForm(request.POST,request.FILES)
        if form.is_valid():
            user = form.save(commit=False)

            user.set_password(
                form.cleaned_data['password']
            )
            user.is_superuser = False
            user.is_staff = False

            user.save()
            return redirect('login')
    else:
        form = registerForm()
    return render(request,'Users/register.html',{'form':form})
def login_view(request):
    if request.method == 'POST':
        form = loginForm(request, data =request.POST)
        if form.is_valid():
            user = form.get_user()

            login(request,user)

            return redirect('home')
    else:
        form = loginForm()
    return render(request,'Users/login.html',{'form':form})

def logout_view(request):
    logout(request)
    return redirect('login')
@login_required
def home(request):
    return render(request,'Users/index.html')
