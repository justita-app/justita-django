from django.urls import path

from social import consumers

websocket_urlpatterns = [
    path("ws/online-counseling/<identity>/", consumers.OnlineCounselingConsumer.as_asgi()),
    path("ws/free-counseling/<identity>/", consumers.FreeCounselingConsumer.as_asgi()),
    path("ws/complaint/<identity>/", consumers.ComplaintRoomConsumer.as_asgi()),
    path("ws/contract/<identity>/", consumers.ContractRoomConsumer.as_asgi()),
    path("ws/legal-panel/<identity>/", consumers.LegalPanelConsumer.as_asgi()),
    path("ws/support/<identity>/", consumers.SupportRoomConsumer.as_asgi()),
]