"""MyProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from MyApp import views as v

urlpatterns = [
    path('admin/', admin.site.urls, name="admin"),
    path('', v.LandingPageView.as_view(), name="landing-page"),
    path('add_donation/', v.AddDonationView.as_view(), name="add-donation"),
    path('success/', v.AddDonationConfirmationView.as_view(), name="form-confirmation"),
    path('register/', v.RegisterView.as_view(), name="register"),
    path('login/', v.LoginView.as_view(), name="login"),
    path('logout/', v.LogoutView.as_view(), name="logout"),
    path('profile/', v.UserProfileView.as_view(), name="user-profile"),
    path('your_donations/', v.UserDonationView.as_view(), name="user-donations"),
    path('profile/modify/', v.UserProfileModifyView.as_view(), name="user-profile-modify"),
    path('profile/confirm/', v.UserProfileModifyAccessView.as_view(), name="user-profile-modify-access"),
    path('confirmation/', v.UserConfirmationsView.as_view(), name="user-confirmation"),
    path('verify/<slug:link>/', v.UserRegisterVerifyActivateLinkView.as_view(), name="verify-activation-link"),
    path('password/remind/', v.UserRemindPasswordView.as_view(), name="remind-password"),
    path('password/reset/<slug:link>/', v.UserPasswordResetView.as_view(), name="reset-password"),

]
