import secrets
import string
from django.core.mail import send_mail
from django.conf import settings


def generate_verification_code(length=6):
    alphabet = string.ascii_letters + string.digits
    code = ''.join(secrets.choice(alphabet) for _ in range(length))
    return code


def send_verification_email(user):
    subject = f'Xác nhận đăng ký tài khoản {user.username}'
    message = f'Mã xác nhận của bạn là: {generate_verification_code}'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])