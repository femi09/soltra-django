from django.urls import path
from authentication.views import AuthenticationViewSet, ChangePasswordView, ForgotPasswordView, ResetPaswordView, ConfirmEmalView, GetVerificationTokenView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('register', AuthenticationViewSet.as_view({'post': 'create'}), name='register_user'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login', AuthenticationViewSet.as_view({'post': 'login'}), name='login_user'),
    path('change-password', ChangePasswordView.as_view(), name='change_password' ),
    path('forgot-password', ForgotPasswordView.as_view(), name='forgot_password' ),
    path('reset-password', ResetPaswordView.as_view(), name="reset_password"),
    path('verify-email', ConfirmEmalView.as_view(), name='verify_email'),
    path('get-verification-token', GetVerificationTokenView.as_view(), name='get_verification_token')
]