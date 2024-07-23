import secrets
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.conf import settings
from oauth2_provider.models import AccessToken, RefreshToken
from datetime import timedelta
from oauth2_provider.oauth2_backends import OAuthLibCore
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.contrib.auth.hashers import check_password

def check_client_secret(stored_secret, provided_secret):
    return check_password(provided_secret, stored_secret)

def refresh_access_token(refresh_token_value):
    try:
        # Fetch the RefreshToken object using the token value
        refresh_token_obj = RefreshToken.objects.get(token=refresh_token_value)
    except RefreshToken.DoesNotExist:
        return None, 'Invalid refresh token'

    # Create a new access token
    try:
        # Use the OAuthLibCore to generate a new access token
        oauth2_backend = OAuthLibCore()
        new_access_token = oauth2_backend.create_access_token(
            user=refresh_token_obj.user,
            application=refresh_token_obj.application,
            scope=refresh_token_obj.scope
        )
    except Exception as e:
        return None, str(e)

    # Save the new access token
    access_token = AccessToken.objects.create(
        user=refresh_token_obj.user,
        application=refresh_token_obj.application,
        token=new_access_token.token,
        expires=timezone.now() + timedelta(seconds=settings.OAUTH2_PROVIDER['ACCESS_TOKEN_EXPIRE_SECONDS']),
        scope=refresh_token_obj.access_token.scope
    )

    return access_token, None



def generate_verification_code(length=6):
    alphabet = string.ascii_letters + string.digits
    code = ''.join(secrets.choice(alphabet) for _ in range(length))
    return code


def send_verification_email(user):
    subject = f'Xác nhận đăng ký tài khoản {user.username}'
    message = f'Mã xác nhận của bạn là: {generate_verification_code}'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])