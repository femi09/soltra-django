from ast import Not
import email
from django.shortcuts import render
from rest_framework import status, generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from authentication.serializers import RegisterUserSerializer, UserSerializer, ChangePasswordSerializer
from django.contrib.auth.hashers import check_password
from django.contrib.sites.shortcuts import get_current_site
from .models import User
from authentication.utils.token import account_activation_token
from helpers.redis import redis_utils

# Create your views here.


class AuthenticationViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # generate random
            token = account_activation_token.make_token(user)

            # store token in redis
            redis_utils.set_value(f'verification_token-{email}', token, 60)

            site = get_current_site(request)

            verify_email_url = f'http://{site}/auth/verification?token={token}'

            return Response({'msg': 'user created successfully', 'data': 'An email to verify your account has been sent to you'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST, exception=True)

    def login(self, request, *args, **kwargs):
        if not request.data:
            return Response({"msg": "please provide email and password"}, status=status.HTTP_400_BAD_REQUEST)
        email = request.data['email']
        password = request.data['password']
        try:
            # find user by email
            user = User.objects.get(email__iexact=email)

            # valid user's password
            valid_password = check_password(password, user.password)

            if not valid_password:
                return Response({"msg": "invalid email or passsord", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

            if not user.email_confirmed:
                return Response({"msg": 'please verify your account to login', "status": status.HTTP_401_UNAUTHORIZED}, status=status.HTTP_401_UNAUTHORIZED)

            # generate access token
            refresh = RefreshToken.for_user(user)
            jwt_token = {
                'token': str(refresh.access_token),
                'refereshToken': str(refresh.access_token),
            }

            return Response({"msg": "login successful", "status": status.HTTP_200_OK, "data": jwt_token}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"msg": "invalid email or passsord",  "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)


class ConfirmEmalView(APIView):
    def post(self, request, *args, **kwargs):
        verification_token = request.data['verification_token']
        email = request.data['email']

        try:
            user = User.objects.get(email__iexact=email)
            # get token from redis
            redis_token = redis_utils.get_value(f'verification_token-{email}')
            decoded_redis_token = redis_token.decode(
                'utf8') if redis_token else None

            if decoded_redis_token != verification_token:
                return Response({"msg": "invalid token! your token may have expired", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

            user.email_confirmed = True
            user.save()

            return Response({"msg": "account verification is successful!", "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"msg": "user not found", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        callback_url = request.data.get('callback_url')
        try:
            user = User.objects.get(email__iexact=email)

            # generate random
            token = account_activation_token.make_token(user)

            #store in redis
            redis_utils.set_value(f'reset_token-{email}', token, 60)

            new_callback_url = f"{callback_url}/{token}"

            print(new_callback_url)

            # send email
            msg = f'An email to reset your password has been sent to {email}'

            return Response({"msg": msg, "data": {"callback_url": new_callback_url}, "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"msg": "invalid email", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)


class ResetPaswordView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data['email']
        password = request.data['password']
        confirm_password = request.data['confirm_password']
        reset_token = request.data['reset_token']

        try:
            user = User.objects.get(email__iexact=email)
            checked_token = account_activation_token.check_token(
                user, reset_token)

            if password != confirm_password:
                return Response({"msg": "password must match", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

            # get token from redis
            redis_token = redis_utils.get_value(f'reset_token-{email}')
            decoded_redis_token = redis_token.decode(
                'utf8') if redis_token else None

            if not checked_token or decoded_redis_token != reset_token:
                return Response({"msg": "invalid token! your token may have expired", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(password)
            user.save()

            msg = "password reset was successful"

            return Response({"msg": msg, "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"msg": "user not found", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # validate the current password
            if not user.check_password(serializer.data.get('oldPassword')):
                return Response({"msg": "old password is not correct", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
            # save new password
            user.set_password(serializer.data.get('newPassword'))
            user.save()

            return Response({"msg": "passord reset is successful", "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)
        return Response({"msg": "validation error", "status": status.HTTP_400_BAD_REQUEST, "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class GetVerificationTokenView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        try:
            user = User.objects.get(email__iexact=email)
            
            if user.email_confirmed:
                return Response({"msg": "account already verified, please log in", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

            # generate random
            token = account_activation_token.make_token(user)

            #store in redis
            redis_utils.set_value(f'verification_token-{email}', token, 60)

            # send email
            site = get_current_site(request)

            verify_email_url = f'http://{site}/auth/verification?token={token}'

            msg = f'An email to verify your account has been sent to {email}'

            return Response({"msg": msg, "status": status.HTTP_200_OK, "data": verify_email_url}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"msg": "invalid email", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
