from apis_acdhch_default_settings.settings import *

INSTALLED_APPS[INSTALLED_APPS.index("apis_ontology")] = "apis_instance_nsvis"
INSTALLED_APPS += ["auditlog"]
INSTALLED_APPS += ["apis_core.history"]
INSTALLED_APPS += ["apis_core.documentation"]
INSTALLED_APPS.insert(0, "apis_core.relations")
INSTALLED_APPS.insert(0, "apis_core.collections")
INSTALLED_APPS += ["apis_acdhch_django_invite"]

ROOT_URLCONF = "apis_instance_nsvis.urls"
