
from django.contrib import admin
from django.urls import path , include
from social import views

app_name = "social"
urlpatterns = [
    path('', views.Home , name="home"),
    path('orders' , views.OrdersView , name="orders"),
    path('chats' , views.ChatsView , name="chats"),
    path('legal-panel' , views.LegalPanelView , name="legal-panel"),
    path('legal-panel-start' , views.LegalPanelRoomStartView , name="legal-panel-start"),
    path('support/' , views.SupportView , name="support"),

    path('chat/online-counseling/<identity>' , views.OnlineCounselingRoomView , name="online-counseling-chat"),
    path('chat/free-counseling/' , views.FreeCounselingView , name="free-counseling"),
    path('chat/free-counseling/<identity>' , views.FreeCounselingRoomView , name="free-counseling-chat"),
    path('chat/complaint/' , views.ComplaintView , name="complaint"),
    path('chat/complaint/<identity>' , views.ComplaintRoomView , name="complaint-room"),
    path('chat/contract/' , views.ContractView , name="contract"),
    path('chat/contract/<identity>' , views.ContractRoomView , name="contract-room"),
    path('chat/legal-panel/<identity>' , views.LegalPanelRoomView , name="legal-panel-chat"),
    path('support/<identity>' , views.SupportRoomView , name="support-room"),
    path('dselect-lawyer/', views.select_lawyer, name='select_lawyer'),
    path('dselect-lawyer-online/', views.select_lawyer_online, name='select_lawyer_online'),
    path('submit-review/', views.submit_review, name='submit_review'),
]
