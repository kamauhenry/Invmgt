import typing_extensions
from django.contrib import admin


from app.models import *



admin.site.register(sqlserverconn)
admin.site.register(IssueItem)
admin.site.register(GroupedItems)
admin.site.register(Custom_UOM)
admin.site.register(Person)
admin.site.register(Labour)
admin.site.register(Tenant)
admin.site.register(CustomUser)




