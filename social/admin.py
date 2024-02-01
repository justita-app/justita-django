from django.contrib import admin
from social.models import CallCounseling , CallCounselingFiles , OnlineCounseling , OnlineCounselingRoom , OnlineCounselingRoomMessage \
    , FreeCounselingRoom , FreeCounselingRoomMessage , ComplaintRoom , ComplaintRoomMessage , ContractRoom , ContractRoomMessage, LegalPanel , LegalPanelMessage \
    , SupportRoom , SupportRoomMessage


class OnlineCounselingMessageAdmin(admin.ModelAdmin) :
    list_display = ["sender" , "created_at"]


admin.site.register(CallCounseling)
admin.site.register(CallCounselingFiles)
admin.site.register(OnlineCounseling)
admin.site.register(OnlineCounselingRoom)
admin.site.register(OnlineCounselingRoomMessage , OnlineCounselingMessageAdmin)
admin.site.register(FreeCounselingRoom)
admin.site.register(FreeCounselingRoomMessage)
admin.site.register(ComplaintRoom)
admin.site.register(ComplaintRoomMessage)
admin.site.register(ContractRoom)
admin.site.register(ContractRoomMessage)
admin.site.register(LegalPanel)
admin.site.register(LegalPanelMessage)
admin.site.register(SupportRoom)
admin.site.register(SupportRoomMessage)