from django.contrib import admin
from .models import *
admin.site.register(LeaveMaster)
admin.site.register(PartialLeaveConverter)
admin.site.register(LeaveGroup)
admin.site.register(LeaveGroupSettings)
admin.site.register(LeaveRestriction)
admin.site.register(LeaveEntry)
admin.site.register(LeaveAvail)
admin.site.register(LeaveRemaining)
admin.site.register(LeaveApprovalComment)
