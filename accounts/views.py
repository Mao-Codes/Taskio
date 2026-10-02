#from django.shortcuts import render

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import SignUpForm


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


@login_required
def home(request):
    if request.user.is_client:
        return redirect("portal:dashboard")
    return redirect("workspace:dashboard")

def landing(request):
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "landing.html")