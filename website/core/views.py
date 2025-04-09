from django.shortcuts import render

# Create your views here.


def health(request):
    return render(request, "home.html")
