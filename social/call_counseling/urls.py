from django.contrib import admin
from django.urls import path , include
from social.call_counseling import views as call_counseling

app_name = "call-counseling"
urlpatterns = [
    path('', call_counseling.CallCounselingView , name="home"),
    path('<identity>/select-lawyer', call_counseling.CallCounselingSelectLawyerView , name="select-lawyer"),
    path('<identity>/subject-time', call_counseling.CallCounselingSubjectTimeView , name="subject-time"),
    path('<identity>/description', call_counseling.CallCounselingDescriptioinView , name="description"),
    path('<identity>/upload-file', call_counseling.CallCounselingUploadFileView, name='upload-file'),
    path('<identity>/order-detail', call_counseling.CallCounselingDetailView, name='order-detail'),
    path('<identity>/start-payment', call_counseling.CallCounselingPaymentStartView, name='start-payment'),
    path('verify-payment', call_counseling.CallCounselingPaymentVerifyView, name='verify-payment'),
]
