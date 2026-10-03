from .models import *
from rest_framework import serializers

class SignupSerializer(serializers.ModelSerializer):
    contact = serializers.CharField(write_only= True)
    course = serializers.CharField(write_only= True)
    address = serializers.CharField(write_only= True)

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "password", "contact", "course", "address"]
        extra_kwargs={"password": {"write_only":True}}

    def create(self, validated_data):
        contact = validated_data.pop("contact")
        course = validated_data.pop("course")
        address = validated_data.pop('address')

        user = User.objects.create_user(**validated_data)
        Student.objects.create(
            user = user,
            contact = contact,
            course = course,
            address = address
        )
        return user
    
class StudentProfileSerializer(serializers.ModelSerializer): 
    first_name = serializers.CharField(source="user.first_name") 
    last_name = serializers.CharField(source="user.last_name") 
    username = serializers.CharField(source="user.username") 

    class Meta: 
          
        model = Student 
        fields = ["id", "first_name", "last_name", "username", "contact", "course", "address"]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

            #student table data
        instance.contact = validated_data.get("contact",instance.contact)
        instance.course = validated_data.get("course", instance.course)
        instance.address = validated_data.get("address", instance.address)
        instance.save()

            #user table data
        user = instance.user
        user.first_name = user_data.get("first_name", user.first_name)
        user.last_name = user_data.get("last_name", user.last_name)
        user.username = user_data.get("username", user.username)
        user.save()

        return instance
    
class DocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documents
        fields = ["id", "title", "file", "uploaded_at"]
        read_only_fields = ["uploaded_at"]

    



    