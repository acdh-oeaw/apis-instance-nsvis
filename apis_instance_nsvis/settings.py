from pathlib import Path
from apis_acdhch_default_settings.settings import *

INSTALLED_APPS[INSTALLED_APPS.index("apis_ontology")] = "apis_instance_nsvis"
INSTALLED_APPS += ["apis_core.documentation"]
INSTALLED_APPS += ["apis_acdhch_django_invite"]
INSTALLED_APPS += ["django_json_editor_field"]
INSTALLED_APPS += ["django_interval"]
INSTALLED_APPS += ["apis_core.uris"]

ROOT_URLCONF = "apis_instance_nsvis.urls"

LANGUAGE_CODE = "de"

STATIC_ROOT = "/data"

MIDDLEWARE += [  # noqa: F405
    "auditlog.middleware.AuditlogMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "apis_core.generic.middleware.HtmxMessageMiddleware",
]

ADDITIONAL_MODULE_LOOKUP_PATHS = ["apis_instance_nsvis", "apis_acdhch_default_settings"]

CSP_IMG_SRC += ["*.acdh-dev.oeaw.ac.at"]

MAGAZINE_FILE = Path(__file__).parent.parent / "magazines.json"
MAGAZINES_SORTED = Path(__file__).parent.parent / "magazines-sorted.json"
