from rest_framework import serializers
from app.models import *


class GroupedItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta :
        model = GroupedItems
        fields = [ 'id', 'grouped_item', 'total_units', 'total', 'used_units','units_available' ]


class SqlServerConnSerializer(serializers.HyperlinkedModelSerializer):
    grouped_item = GroupedItemSerializer
    class Meta :
        model = sqlserverconn
        fields = ['Item_id', 'Item', 'Item_Description', 'Units', 'Unit_of_measurement','Unit_cost', 'Date', 'Subtotal','grouped_item']


class personSerializer(serializers.HyperlinkedModelSerializer):
    class Meta :
        model = Person
        fields = [ 'person' ]

class IssueItemSerializer(serializers.HyperlinkedModelSerializer):
    grouped_item = GroupedItemSerializer()
    person = personSerializer()
    class Meta :
        model = IssueItem
        fields = ['id','person','grouped_item','units_issued','units_returned','units_used','Date' ]
        
class LabourSerializer(serializers.HyperlinkedModelSerializer):
    class Meta :
        model = Labour
        fields = ['labour_type','NOL','Date ','labourer_cost','sub_total' ]
        
class Custom_UOMSerializer(serializers.HyperlinkedModelSerializer):
    class Meta :
        model = Custom_UOM
        fields = ['UOM']