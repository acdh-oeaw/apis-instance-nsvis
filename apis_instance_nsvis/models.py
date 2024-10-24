from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from apis_core.apis_entities.abc import E53_Place, E21_Person
from apis_core.history.models import VersionMixin
from apis_core.apis_entities.models import AbstractEntity
from apis_core.relations.models import Relation

from auditlog.registry import auditlog


class NsvisMixin:
    pass


class MongoDbModel(models.Model):
    data = models.JSONField()
    filename = models.TextField(blank=False, max_length=32)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")


class MongoDbDataMixin:
    mongodbdata = GenericRelation(MongoDbModel)


class Person(E21_Person, AbstractEntity, VersionMixin, MongoDbDataMixin):
    biography = models.TextField(blank=True, verbose_name=_("Biography"))


class Place(E53_Place, AbstractEntity, VersionMixin, MongoDbDataMixin):
    pass


class Institution(AbstractEntity, VersionMixin, MongoDbDataMixin):
    """ Zeitschriften, Verlage, Agenturen, Partei + Vorfeldorganisation """
    label = models.CharField(blank=True, default="", max_length=4096, verbose_name=_("Label"))

    def __str__(self):
        return self.label


class AddressData(AbstractEntity, VersionMixin):
    postal = models.TextField(blank=True, max_length=32, verbose_name=_("Postal"))
    address = models.TextField(blank=True, max_length=64, verbose_name=_("Address"))


auditlog.register(Person, serialize_data=True)
auditlog.register(Place, serialize_data=True)
auditlog.register(Institution, serialize_data=True)
auditlog.register(AddressData, serialize_data=True)


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


class AddressInPlace(Relation):
    subj_model = AddressData
    obj_model = Place


auditlog.register(Collaboration)
auditlog.register(Membership)
auditlog.register(LivesIn)
auditlog.register(WorksIn)
auditlog.register(AddressInPlace)
