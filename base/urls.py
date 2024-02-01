from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



app_name = "base"
urlpatterns = [
    # can work 
    path('',views.home, name='home' ),
    path('about',views.about ,name="about"),
    path('english-about',views.aboutEng ,name="about_eng"),
    path('online-attorney',views.online_attorney ,name="online-atterney"),
    path('call-counseling-lawyer' , views.ccl , name="ccl"),

    # need to fix 
 
]