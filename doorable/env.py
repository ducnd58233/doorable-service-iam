import os
import environ
from django.core.exceptions import ImproperlyConfigured
from pathlib import Path

env = environ.Env(
    DEBUG=(bool, False),
)

BASE_DIR = Path(__file__).resolve().parent.parent

env.read_env(os.path.join(BASE_DIR, ".env"))

def env_to_enum(enum_cls, value):
    for x in enum_cls:
        if x.value == value:
            return x
    
    raise ImproperlyConfigured(f"Env value {repr(value)} could not be found in {repr(enum_cls)}")
