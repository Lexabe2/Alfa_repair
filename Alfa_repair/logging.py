import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # Отключение текущих логов
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'formatters': {
        'simple': {
            'format': '{levelname} {asctime:s} {name} {message}',
            'style': '{'
        },
        'verbose': {
            'format': '{levelname} {asctime} {name} {module}.py (line {lineno}) {funcName} {message}',
            'style': '{'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': BASE_DIR / 'debug.log',
        }
    },
    'loggers': {
        "": {
            'level': 'DEBUG',
            'handlers': ["console", "file"],
        },
    },
}
