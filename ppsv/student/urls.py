"""
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path
from . import views

app_name = "student"

urlpatterns = [
    path('', views.Overview.as_view(), name="overview"),
    path('complete-profile', views.CompleteProfileView.as_view(), name="complete-profile"),
    path('edit-profile', views.EditProfileView.as_view(), name="edit-profile"),
    path('register', views.RegisterView.as_view(), name="register"),
    path('registration/<int:pk>/select-topics', views.EditRegistrationView.as_view(), name="register-select-topics"),
    path('registration/<int:pk>/edit-members', views.EditGroupView.as_view(), name="register-edit-group"),
    path('registration/<int:pk>/withdraw', views.WithdrawRegistrationView.as_view(), name="register-withdraw"),
    path('403', views.LoginRequiredView.as_view(), name="login-required"),
]
