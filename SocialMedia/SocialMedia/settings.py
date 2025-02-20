"""
Django settings for SocialMedia project.

Generated by 'django-admin startproject' using Django 5.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-dtn_+61n9is#9@&*yh94t)*n1li_p&cfni$a&5$m!fn%4=zxj_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['hoang3ber123.pythonanywhere.com', 'localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'SocialMediaApp.apps.SocialmediaappConfig',
    'corsheaders',
    'rest_framework',
    'oauth2_provider',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'corsheaders.middleware.CorsMiddleware', #Cấu hình cors cho phép người dùng có thể fetapi dù khác domain
]
CORS_ALLOW_ALL_ORIGINS = True


ROOT_URLCONF = 'SocialMedia.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

MEDIA_ROOT = '%s/SocialMediaApp/static/' % BASE_DIR
WSGI_APPLICATION = 'SocialMedia.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

import pymysql
pymysql.install_as_MySQLdb()
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'smdb',
        'USER':'root',
        'PASSWORD':'Admin@123',
        'HOST':''
    }
}
AUTH_USER_MODEL = 'SocialMediaApp.User'


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Ho_Chi_Minh'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

# Thiết lập SMTP cho gửi email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Ví dụ: smtp.gmail.com
EMAIL_PORT = 587  # Port của email host, ví dụ: Gmail sử dụng 587 cho TLS
EMAIL_USE_TLS = True  # Sử dụng TLS để bảo mật kết nối
EMAIL_HOST_USER = 'Hoangtestmail123@gmail.com'  # Địa chỉ email của bạn
EMAIL_HOST_PASSWORD = 'Hoang@0907198643'  # Mật khẩu email của bạn

#AUTHENTICATION BACKEND
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'oauth2_provider.backends.OAuth2Backend',
)

OAUTH2_PROVIDER = {
    'ACCESS_TOKEN_EXPIRE_SECONDS': 86400,
    'REFRESH_TOKEN_EXPIRE_SECONDS': 86400*7,#refreshtoken 7 ngày
    'ROTATE_REFRESH_TOKEN': True,
}


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CLIENT_ID="NxgQmin8CgbpJPczgLZOTavcAZL1y18dZmmvFyxp"
CLIENT_SECRECT="9SqtdFVxidDiK0VPfC1FEQbr69zOHbFuKta4XTAPfSfdhIsl6evan2357ltDDoAc2rgbwpG7sDnTVkjRjI4QQElk0b7fGcDPyD2kJd3SzNxZdAzDxVPFZPlakMY7Iv09Y"