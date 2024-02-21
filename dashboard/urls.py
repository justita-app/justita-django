from django.urls import path
from . import views


app_name = 'dashboard'
urlpatterns = [
    path('' , views.dashboardView , name='dashboard'),
    path('support/' , views.supportRoomView , name='support'),
    path('chats/' , views.ChatRoomsView , name='chats'),
    path('users/' , views.UsersView , name='users')
]