from django.contrib import admin
from django.urls import path , include
from social.online_counseling import views as online_counseling

app_name = "online-counseling"
urlpatterns = [
    path('', online_counseling.OnlineCounselingView , name="home"),
    path('<identity>/select-lawyer', online_counseling.OnlineCounselingSelectLawyerView , name="select-lawyer"),
    path('<identity>/chat-preview', online_counseling.OnlineCounselingChatPreviewView , name="chat-preview"),
    path('<identity>/start-payment', online_counseling.OnlineCounselingPaymentStartView , name="start-payment"),
    path('verify-payment', online_counseling.OnlineCounselingPaymentVerifyView, name='verify-payment'),
]
