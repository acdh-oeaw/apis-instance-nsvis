from apis_acdhch_default_settings.settings import *

INSTALLED_APPS[INSTALLED_APPS.index("apis_ontology")] = "apis_instance_nsvis"
INSTALLED_APPS += ["auditlog"]
INSTALLED_APPS.insert(0, "apis_core.relations")
