from apis_core.apis_entities.abc import E53_Place, E21_Person
from apis_core.generic.abc import GenericModel
from apis_core.history.models import VersionMixin

from auditlog.registry import auditlog


class NsvisMixin:
    pass


class Person(E21_Person, GenericModel, VersionMixin):
    pass


class Place(E53_Place, GenericModel, VersionMixin):
    pass


class Institution(GenericModel, VersionMixin):
    pass


auditlog.register(Person, serialize_data=True)
auditlog.register(Place, serialize_data=True)
auditlog.register(Institution, serialize_data=True)
