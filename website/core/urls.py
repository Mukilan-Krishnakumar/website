from django.urls import path
from core import views

urlpatterns = [
    path("", views.HomePageView.as_view()),
    path("<str:slug>", views.StaticSiteView.as_view()),
]
