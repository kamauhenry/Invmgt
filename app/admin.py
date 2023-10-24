from django.contrib import admin


from app.models import Custom_UOM, GroupedItems, IssueItem, Person,  sqlserverconn, Labour



admin.site.register(sqlserverconn)
admin.site.register(IssueItem)
admin.site.register(GroupedItems)
admin.site.register(Custom_UOM)
admin.site.register(Person)
admin.site.register(Labour)
