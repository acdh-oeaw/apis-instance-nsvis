from apis_core.apis_entities.abc import E53_Place, E21_Person
from apis_core.history.models import VersionMixin
from apis_core.apis_entities.models import AbstractEntity

from auditlog.registry import auditlog


class NsvisMixin:
    pass


class Person(E21_Person, AbstractEntity, VersionMixin):
    pass


class Place(E53_Place, AbstractEntity, VersionMixin):
    pass


class Institution(AbstractEntity, VersionMixin):
    pass


auditlog.register(Person, serialize_data=True)
auditlog.register(Place, serialize_data=True)
auditlog.register(Institution, serialize_data=True)
