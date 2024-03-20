from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



app_name = "base"
urlpatterns = [
    
    path('',views.home, name='home' ),

    path('online-attorney',views.online_attorney ,name="online-atterney"),
    path('call-counseling-lawyer' , views.ccl , name="ccl"),
    path('download' , views.download , name="download"),
    path('terms-of-service' , views.tos , name="tos"),

   
 
]