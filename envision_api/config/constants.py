import os
from dotenv import load_dotenv
from enum import Enum

load_dotenv()


class EnvironmentEnum(Enum):
    production = 'production'
    development = 'development'
    test = 'test'

    @classmethod
    def _missing_(cls, value):
        return cls.test


CURRENT_ENVIRONMENT = EnvironmentEnum(os.getenv('CURRENT_ENVIRONMENT'))
MONGODB_USER = os.getenv('MONGODB_USER')
MONGODB_PASSWD = os.getenv('MONGODB_PASSWD')
MONGO_URI_TEST = os.getenv('MONGO_URI_TEST')
API_KEY = os.getenv('API_KEY')
ENVISION_APP_API_KEY = os.getenv('ENVISION_APP_API_KEY')
THINKIFIC_API_KEY = os.getenv('THINKIFIC_API_KEY')
THINKIFIC_SUBDOMAIN = os.getenv('THINKIFIC_SUBDOMAIN')
CMS_API_KEY = os.getenv('CMS_API_KEY')
CMS_SITE_ID = os.getenv('CMS_SITE_ID')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET')
MAILCHIMP_KEY = os.getenv('MAILCHIMP_KEY')
FRONTEND_URL = os.getenv('FRONTEND_URL')
BACKEND_URL = os.getenv('BACKEND_URL')
JWT_SECRET = os.getenv('JWT_SECRET') if CURRENT_ENVIRONMENT != EnvironmentEnum.test else 'test jwt secret'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
