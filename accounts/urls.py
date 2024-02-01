from django.urls import path
from . import views


app_name = "accounts"

urlpatterns = [
    path('', views.AccountView , name="home"),
    path('login/',views.LoginView ,name="login"),
    path('register/<identity>/',views.RegisterView ,name="register"),
    path('logout/',views.LogoutView ,name="logout"),
    path('sms-verify/<phone_number>/',views.SmsVerifyView ,name="sms-verify"),
    path('change-phonenumber/',views.ChangePhoneNumberView ,name="change-phonenumber"),
    path('change-phonenumber/<phone_number>/validation',views.ChangePhoneNumberVerificationView ,name="change-phonenumber_validation"),
]