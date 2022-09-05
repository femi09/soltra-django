from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        """Access fields and create returned object."""
        model = User
        fields = '__all__'
        extra_kwargs = {
            "password": {"write_only": True},
        }


class RegisterUserSerializer(serializers.ModelSerializer):
    """
      Customer Model Serializer.
    """
    confirmPassword = serializers.CharField(
        style={"input-type": 'password'}, write_only=True)
    
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = [
            'id',
            'name',
            'email',
            'phone_number',
            'password',
            'confirmPassword',
        ]
        extra_kwargs = {
            'password': {"write_only": True}
        }

    def save(self):
        email_field = self.validated_data['email']
        email = email_field.lower()
        
        # print("validated data", self.validated_data)

        user = User(
            email=email, name=self.validated_data['name'], phone_number=self.validated_data['phone_number'])
        password  = self.validated_data['password']
        confirmPassword = self.validated_data['confirmPassword']
        
        if password != confirmPassword:
            raise serializers.ValidationError({"msg":"Password must match"})
        
        # hash the user's password
        user.set_password(password)
        user.save()
        return user
    
    
class ChangePasswordSerializer(serializers.ModelSerializer):
    """
    Serializer for password change endpoint.
    """
    oldPassword = serializers.CharField(required=True)
    newPassword = serializers.CharField(required=True)
    confirmPassword = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ['oldPassword', 'confirmPassword', 'newPassword']
            
    def validate(self, validated_data):
        newPassword = validated_data.get('newPassword')
        confirmPassword = validated_data.get('confirmPassword')
        print('new password', newPassword)
        print('confirm password', confirmPassword)
        if newPassword != confirmPassword:
            raise serializers.ValidationError({"msg":"password must match"})
        return validated_data