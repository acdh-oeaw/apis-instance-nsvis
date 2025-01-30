from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from apis_core.apis_entities.abc import E53_Place
from apis_core.history.models import VersionMixin
from apis_core.apis_entities.models import AbstractEntity
from apis_core.relations.models import Relation
from django.contrib.postgres.fields import ArrayField
from django_interval.fields import FuzzyDateParserField

from auditlog.registry import auditlog


class NsvisMixin:
    pass


class MongoDbModel(models.Model):
    data = models.JSONField()
    filename = models.TextField(blank=False, max_length=32)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey("content_type", "object_id")


class MongoDbDataMixin(models.Model):
    mongodbdata = GenericRelation(MongoDbModel)

    class Meta:
        abstract = True


class Person(AbstractEntity, VersionMixin, MongoDbDataMixin):
    forename = models.CharField(blank=True, default="", max_length=4096)
    surname = models.CharField(blank=True, default="", max_length=4096)
    gender = models.CharField(blank=True, default="", max_length=4096)
    date_of_birth = FuzzyDateParserField(blank=True, null=True)
    date_of_death = FuzzyDateParserField(blank=True, null=True)

    def __str__(self):
        return f"{self.forename} {self.surname}"


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

    def __str__(self):
        return f"{self.address} ({self.postal})"


class Annotation(AbstractEntity):
    data = models.JSONField(null=True, editable=False)
    image = models.TextField(max_length=512, editable=False)
    issue = models.TextField(max_length=256, editable=False)
    lst_task_id = models.IntegerField(editable=False)
    lst_annotation_id = models.IntegerField(editable=False)
    lst_result_id = models.TextField(max_length=128, editable=False)

    author = ArrayField(models.CharField(), null=True)
    caption = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    depicted = ArrayField(models.CharField(), null=True)
    location = models.TextField(blank=True, null=True)
    topic = ArrayField(models.CharField(), null=True)
    other = models.TextField(blank=True, null=True)
    internal_comment = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('lst_task_id', 'lst_annotation_id', "lst_result_id"),)

    def __str__(self):
        if label := self.data.get("iiif_label"):
            return f"{self.issue} ({label}) [{self.lst_result_id}]"
        return self.issue


auditlog.register(Person, serialize_data=True)
auditlog.register(Place, serialize_data=True)
auditlog.register(Institution, serialize_data=True)
auditlog.register(AddressData, serialize_data=True)


class TimespanMixin(models.Model):
    from_date = FuzzyDateParserField(blank=True, null=True)
    to_date = FuzzyDateParserField(blank=True, null=True)

    class Meta:
        abstract = True


class CollaboratesWith(Relation):
    subj_model = Person
    obj_model = Person


class IsMemberOf(TimespanMixin, Relation):
    subj_model = Person
    obj_model = Institution

    @classmethod
    def name(self) -> str:
        return "is member of"

    @classmethod
    def reverse_name(self) -> str:
        return "has as member"


class IsInventoriedIn(Relation):
    subj_model = Person
    obj_model = Institution

    @classmethod
    def name(self) -> str:
        return "is inventoried in"

    @classmethod
    def reverse_name(self) -> str:
        return "inventories"


class IsLearningAt(TimespanMixin, Relation):
    subj_model = Person
    obj_model = Institution


class LivesIn(TimespanMixin, Relation):
    subj_model = Person
    obj_model = [Place, AddressData]


class HasStudioIn(TimespanMixin, Relation):
    subj_model = Person
    obj_model = [Place, AddressData]


class WorksIn(Relation):
    subj_model = Person
    obj_model = Place


class AddressInPlace(Relation):
    subj_model = AddressData
    obj_model = Place


class BornIn(Relation):
    subj_model = Person
    obj_model = Place


class DiedIn(Relation):
    subj_model = Person
    obj_model = Place


auditlog.register(CollaboratesWith)
auditlog.register(IsMemberOf)
auditlog.register(IsInventoriedIn)
auditlog.register(IsLearningAt)
auditlog.register(LivesIn)
auditlog.register(WorksIn)
auditlog.register(AddressInPlace)
