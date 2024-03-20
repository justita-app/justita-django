from django.urls import path
from . import views


app_name = "accounts"

urlpatterns = [
    path('', views.AccountView , name="home"),
    path('login/',views.LoginView ,name="login"),
    path('lawyer-login/',views.LawyerLoginView ,name="lawyer-login"),
    path('register/<identity>/',views.RegisterView ,name="register"),
    path('lawyer-register/<identity>/',views.LawyerRegisterView ,name="lawyer-register"),
    path('logout/',views.LogoutView ,name="logout"),
    path('sms-verify/<phone_number>/',views.SmsVerifyView ,name="sms-verify"),
    path('lawyer-sms-verify/<phone_number>/',views.LawyerSmsVerifyView ,name="lawyer-sms-verify"),
    path('change-phonenumber/',views.ChangePhoneNumberView ,name="change-phonenumber"),
    path('change-phonenumber/<phone_number>/validation',views.ChangePhoneNumberVerificationView ,name="change-phonenumber_validation"),
]