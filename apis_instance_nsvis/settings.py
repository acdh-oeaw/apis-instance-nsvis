from apis_acdhch_default_settings.settings import *

INSTALLED_APPS[INSTALLED_APPS.index("apis_ontology")] = "apis_instance_nsvis"
INSTALLED_APPS += ["auditlog"]
INSTALLED_APPS += ["apis_core.history"]
INSTALLED_APPS += ["apis_core.documentation"]
INSTALLED_APPS.insert(0, "apis_core.relations")
INSTALLED_APPS.remove("apis_core.apis_relations")
