from rest_framework import serializers


class LookupsSerializer(serializers.Serializer):
    display_value = serializers.CharField(max_length=200)
    key_value = serializers.IntegerField()
