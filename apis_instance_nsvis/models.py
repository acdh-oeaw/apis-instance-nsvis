from django.db import models
from django.utils.translation import gettext_lazy as _
from apis_core.apis_entities.abc import E53_Place, E21_Person
from apis_core.history.models import VersionMixin
from apis_core.apis_entities.models import AbstractEntity
from apis_core.relations.models import Relation

from auditlog.registry import auditlog


class NsvisMixin:
    pass


class Person(E21_Person, AbstractEntity, VersionMixin):
    biography = models.TextField(blank=True, verbose_name=_("Biography"))

    pass


class Place(E53_Place, AbstractEntity, VersionMixin):
    pass


class Institution(AbstractEntity, VersionMixin):
    """ Zeitschriften, Verlage, Agenturen, Partei + Vorfeldorganisation """
    pass


auditlog.register(Person, serialize_data=True)
auditlog.register(Place, serialize_data=True)
auditlog.register(Institution, serialize_data=True)


class Collaboration(Relation):
    subj_model = Person
    obj_model = Person


class Membership(Relation):
    subj_model = Person
    obj_model = Institution


class LivesIn(Relation):
    subj_model = Person
    obj_model = Place


class WorksIn(Relation):
    subj_model = Person
    obj_model = Place
