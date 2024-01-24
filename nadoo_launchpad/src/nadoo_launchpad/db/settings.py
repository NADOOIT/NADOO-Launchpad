import os
from pathlib import Path
import django
from dotenv import load_dotenv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = Path(__file__).resolve() / ".env"

# Load the .env file into the environment. This is done before the settings are loaded.
# This is done to make sure that the environment variables are available when the settings are loaded.
# Was required to make the environment variables available in the test_services.py file.
load_dotenv(dotenv_path=ENV_FILE)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "changeme")

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db", "db.sqlite3"),
    }
}


"""
To connect to an existing postgres database, first:
pip install psycopg2
then overwrite the settings above with:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'YOURDB',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
    }
}
"""

INSTALLED_APPS = ("db",)
