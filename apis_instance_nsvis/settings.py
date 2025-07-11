from pathlib import Path
from apis_acdhch_default_settings.settings import *

INSTALLED_APPS[INSTALLED_APPS.index("apis_ontology")] = "apis_instance_nsvis"
INSTALLED_APPS += ["apis_core.documentation"]
INSTALLED_APPS += ["apis_acdhch_django_invite"]
INSTALLED_APPS += ["django_json_editor_field"]
INSTALLED_APPS += ["django_interval"]

ROOT_URLCONF = "apis_instance_nsvis.urls"

LANGUAGE_CODE = "de"

STATIC_ROOT = "/images"

MIDDLEWARE += [  # noqa: F405
    "auditlog.middleware.AuditlogMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

ADDITIONAL_MODULE_LOOKUP_PATHS = ["apis_instance_nsvis", "apis_acdhch_default_settings"]
