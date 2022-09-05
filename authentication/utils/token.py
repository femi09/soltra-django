from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type
import math
import random

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp) -> str:
        return (
            text_type(user.pk) + text_type(timestamp) + text_type(user.is_active)
        )
        
    def generate_otp(self):
        digits = '0123456789'
        OTP = ''
        
        for _ in range(6):
            OTP += digits[math.floor(random.random() * 10)]
        return OTP
    
account_activation_token = TokenGenerator()