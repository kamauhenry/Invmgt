from django.contrib import admin


from app.models import GroupedItems, IssueItem, sqlserverconn



admin.site.register(sqlserverconn)
admin.site.register(IssueItem)
admin.site.register(GroupedItems)
