from django.urls import path
from . import views


app_name = 'lawyers'
urlpatterns = [
    path('' , views.lawyers , name='lawyers'),
    path('settings/' , views.settings , name='settings'),
    path('personal-settings/' , views.personal_settings , name='personal-settings'),
    path('verification/' , views.verification , name='verification'),
    path('pricings/' , views.pricings , name='pricings'),
    path('financial/' , views.financial , name='financial'),
    path('council/' , views.councilView , name='council'),
    path('chats/' , views.ChatRoomsView , name='chats'),

    # API Views
    path("update-status/", views.UpdateStatus.as_view(), name="update-status"),
]