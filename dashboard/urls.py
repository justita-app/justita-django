from django.urls import path
from . import views


app_name = 'dashboard'
urlpatterns = [
    path('' , views.dashboardView , name='dashboard'),
    path('allcalls' , views.dashboardViewAll , name='dashboardall'),
    path('support/' , views.supportRoomView , name='support'),
    path('chats/' , views.ChatRoomsView , name='chats'),
    path('users/' , views.UsersView , name='users'),
    path('comments/' , views.Comments , name='comments')
    ]