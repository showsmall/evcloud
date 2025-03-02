"""
Django settings for django_site project.

Generated by 'django-admin startproject' using Django 2.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'w8d+&&ximtq8==j$@h(e6ow896454254#4i!&(vhbbw$s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']
INTERNAL_IPS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',

    'vms',
    'users',
    'api',
    'ceph',
    'compute.apps.ComputeConfig',
    'device',
    'image.apps.ImageConfig',
    'network.apps.NetworkConfig',
    'novnc',
    'vdisk',
    'docs',
    'reports',
    'pcservers',
    'vpn'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), ],
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

WSGI_APPLICATION = 'django_site.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',  # 数据库引擎
#         'NAME': 'xxx',  # 数据的库名，事先要创建之
#         'HOST': 'xx.xx.xx.xx',  # 主机
#         'PORT': '3306',  # 数据库使用的端口
#         'USER': 'xxx',  # 数据库用户名
#         'PASSWORD': 'xxx',  # 密码
#         'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"}
#     },
# }


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
# 上传文件
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'collect_static')
# 静态文件查找路径
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# session 有效期设置
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True      # True：关闭浏览器，则Cookie失效。
# SESSION_COOKIE_AGE=60*30   #30分钟

# 自定义用户模型
AUTH_USER_MODEL = 'users.UserProfile'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# 避免django把未以/结尾的url重定向到以/结尾的url
# APPEND_SLASH=False

# 登陆url
LOGIN_URL = '/users/login/'
LOGOUT_URL = '/users/logout/'
LOGIN_REDIRECT_URL = '/'    # 默认重定向url

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        'rest_framework.permissions.IsAuthenticated',
        # 'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'users.auth.authentication.AuthKeyAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',    # 支持解析application/json方式的json数据
        'rest_framework.parsers.FormParser',    # 支持解析application/x-www-form-urlencoded方式的form表单数据，request.data将填充一个QueryDict
        'rest_framework.parsers.MultiPartParser'     # 支持解析multipart/form-data方式多部分HTML表单内容，支持文件上载，request.data将填充一个QueryDict
    ),
    # 'DEFAULT_THROTTLE_CLASSES': (
    #     'rest_framework.throttling.AnonRateThrottle',  # 未登陆认证的用户默认访问限制
    #     'rest_framework.throttling.UserRateThrottle'  # 登陆认证的用户默认访问限制
    # ),
    # 'DEFAULT_THROTTLE_RATES': {
    #     'anon': '5/minute',  # 未登陆认证的用户默认请求访问限制每分钟次数
    #     'user': '20/minute'  # 登陆认证的用户默认请求访问限制每分钟次数
    # },
    # api version settings
    # 'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    # 'DEFAULT_VERSION': 'v3',
    # 'ALLOWED_VERSIONS': ('v3', ),
    # 'VERSION_PARAM': 'version',

    'EXCEPTION_HANDLER': 'api.viewsets.exception_handler',

    # 分页
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,

    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=2),
    'ROTATE_REFRESH_TOKENS': False,     # True时，refresh API会返回内容中会包含一个新的refresh JWT
    'BLACKLIST_AFTER_ROTATION': True,

    # 'SIGNING_KEY': 'xxxxx',   # 默认SECRET_KEY

    'AUTH_HEADER_TYPES': ('Bearer', 'JWT'),     # Header "Authorization:{AUTH_HEADER_TYPES} xxx"
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# vnc
VNCSERVER_BASE_PORT = 5900
# NOVNC_SERVER_PORT = 84  # novnc代理服务websockify的端口； 默认为80（需要通过nginx代理）

# 日志配置
LOGGING_FILES_DIR = os.path.join('/var/log', os.path.basename(BASE_DIR))
if not os.path.exists(LOGGING_FILES_DIR):
    os.makedirs(LOGGING_FILES_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'dubug_formatter': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
        'user_formatter': {
            'format': '%(levelname)s %(asctime)s %(user_id)d %(username)s %(url)s %(method)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        # logging file settings
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': os.path.join(LOGGING_FILES_DIR, 'webserver.log'),
            'formatter': 'verbose'
        },
        # output to console settings
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],  # working with debug mode
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        # debug logging file settings
        'debug': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],  # working with debug mode
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': os.path.join(LOGGING_FILES_DIR, 'debug.log'),
            'formatter': 'dubug_formatter'
        },
        # 邮件通知
        # 'mail_admins': {
        #     'level': 'ERROR',
        #     'class': 'django.utils.log.AdminEmailHandler',
        #     'filters': ['special']
        # }
        'user_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGGING_FILES_DIR, 'evcloud_user.log'),
            'formatter': 'user_formatter',
            'maxBytes':  1024 * 1024 * 512
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'debug': {
            'handlers': ['debug'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'user': {
            'handlers': ['user_handler', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# drf-yasg
SWAGGER_SETTINGS = {
    # 'LOGIN_URL': reverse_lazy('admin:login'),
    # 'LOGOUT_URL': '/admin/logout',
    'PERSIST_AUTH': True,
    'REFETCH_SCHEMA_WITH_AUTH': True,
    'REFETCH_SCHEMA_ON_LOGOUT': True,


    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        },
        'Bearer': {
            'in': 'header',
            'name': 'Authorization',
            'type': 'apiKey',
        }
    },
}

# 导入安全相关的settings
from .security import *

if DEBUG:
    # django debug toolbar
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    DEBUG_TOOLBAR_CONFIG = {
        # 'SHOW_COLLAPSED': True,
    }
    INTERNAL_IPS += ['159.226.235.2', '159.226.91.152', '127.0.0.1']    # 通过这些IP地址访问时，页面才会出现django debug toolbar面板
