from urllib.parse import urlparse
from pathlib import Path
from PIL import Image
import httpx

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import slugify
from apis_core.apis_entities.abc import E53_Place
from apis_core.history.models import VersionMixin
from apis_core.apis_entities.models import AbstractEntity
from apis_core.relations.models import Relation
from apis_core.generic.abc import GenericModel
from django.contrib.postgres.fields import ArrayField
from django_interval.fields import FuzzyDateParserField
from django_json_editor_field.fields import JSONEditorField

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


class SpecialArea(GenericModel, VersionMixin, MongoDbDataMixin):
    class Meta:
        verbose_name = _("Special Area")
        verbose_name_plural = _("Special Areas")

    label = models.CharField(blank=True, default="", max_length=4096, verbose_name=_("Label"))

    def __str__(self):
        return self.label


class Person(AbstractEntity, VersionMixin, MongoDbDataMixin):
    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")
        ordering = ["surname", "forename"]

    forename = models.CharField(blank=True, default="", max_length=4096, verbose_name=_("Forname"))
    surname = models.CharField(blank=True, default="", max_length=4096, verbose_name=_("Surname"))
    gender = models.CharField(blank=True, default="", max_length=4096, verbose_name=_("Gender"))
    date_of_birth = FuzzyDateParserField(blank=True, null=True, verbose_name=_("Date of birth"))
    date_of_death = FuzzyDateParserField(blank=True, null=True, verbose_name=_("Date of death"))
    citizenship = models.CharField(blank=True, default="", max_length=4096, verbose_name=_("Citizenship"))
    comment = models.TextField(blank=True, default="", verbose_name=_("Comment"))
    membership_comment = models.TextField(blank=True, default="", verbose_name=_("Membership comment"))
    special_areas = models.ManyToManyField(SpecialArea, blank=True, verbose_name=_("Special areas"))
    party_comment = models.TextField(blank=True, default="", verbose_name=_("Party comment"))
    exile_comment = models.TextField(blank=True, default="", verbose_name=_("Exile comment"))
    profession_comment = models.TextField(blank=True, default="", verbose_name=_("Profession comment"))
    schema = {
            "title": "Inheritance",
            "type": "array",
            "format": "table",
            "items": {
                "type": "object",
                "properties": {
                    "contact": {
                        "type": "string",
                        "options": {
                            "inputAttributes": {
                                "placeholder": "contact",
                            }
                        }
                    },
                    "extent": {
                        "type": "string",
                        "options": {
                            "inputAttributes": {
                                "placeholder": "extent",
                            }
                        }
                    },
                    "comment": {
                        "type": "string",
                        "options": {
                            "inputAttributes": {
                                "placeholder": "comment",
                            }
                        }
                    }
                }
            }
        }
    options = {
        "theme": "bootstrap5",
        "disable_collapse": True,
        "disable_edit_json": True,
        "disable_properties": True,
        "disable_array_reorder": True,
        "disable_array_delete_last_row": True,
        "disable_array_delete_all_rows": True,
        "prompt_before_delete": False,
    }
    inheritance = JSONEditorField(schema=schema, options=options, null=True, verbose_name=_("Inheritance"))
    sources_schema = {
            "title": "Sources",
            "type": "array",
            "format": "table",
            "items": {
                "type": "string",
            }
        }
    research_sources = JSONEditorField(schema=sources_schema, options=options, null=True, verbose_name=_("Research sources"))
    other_sources = JSONEditorField(schema=sources_schema, options=options, null=True, verbose_name=_("Other sources"))
    literature = JSONEditorField(schema=sources_schema, options=options, null=True, verbose_name=_("Literature"))

    class Choices(models.TextChoices):
        YES = "YES", _("Yes")
        NO = "NO", _("No")
        UNK = "UNK", _("Unknown")
    work_ban = models.CharField(max_length=8, choices=Choices, default=Choices.UNK, verbose_name="Work ban during NS")
    work_ns = models.CharField(max_length=9, choices=Choices, default=Choices.UNK, verbose_name="Worked during NS")
    propaganda_membership = models.CharField(max_length=9, choices=Choices, default=Choices.UNK, verbose_name="Member in a propaganda company")

    def __str__(self):
        return f"{self.forename} {self.surname}"


class Place(E53_Place, AbstractEntity, VersionMixin, MongoDbDataMixin):
    class Meta:
        verbose_name = _("Place")
        verbose_name_plural = _("Places")


class Institution(AbstractEntity, VersionMixin, MongoDbDataMixin):
    """ Zeitschriften, Verlage, Agenturen, Partei + Vorfeldorganisation """
    class Meta:
        verbose_name = _("Institution")
        verbose_name_plural = _("Institutions")

    label = models.CharField(blank=True, default="", max_length=4096, verbose_name=_("Label"))

    def __str__(self):
        return self.label


class EducationType(AbstractEntity, VersionMixin, MongoDbDataMixin):
    class Meta:
        verbose_name = _("Education Type")
        verbose_name_plural = _("Education Types")

    label = models.CharField(blank=True, default="", max_length=4096, verbose_name=_("Label"))

    def __str__(self):
        return self.label


class ProfessionType(AbstractEntity, VersionMixin, MongoDbDataMixin):
    class Meta:
        verbose_name = _("Profession Type")
        verbose_name_plural = _("Profession Types")

    label = models.CharField(blank=True, default="", max_length=4096, verbose_name=_("Label"))

    def __str__(self):
        return self.label


class AddressData(AbstractEntity, VersionMixin):
    class Meta:
        verbose_name = _("Address Data")
        verbose_name_plural = _("Address Datas")

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

    def local_image(self):
        headers = {'Origin': "https://label-studio.acdh-dev.oeaw.ac.at"}
        suffix = Path(urlparse(self.image).path).suffix
        issueslug = slugify(self.issue)
        imagepath = Path(settings.STATIC_ROOT) / issueslug / f"{self.lst_result_id}{suffix}"
        if not imagepath.exists():
            imagepath.parent.mkdir(parents=True, exist_ok=True)
            with httpx.stream("GET", self.image, headers=headers) as r:
                if r.status_code == httpx.codes.OK:
                    for data in r.iter_bytes():
                        with imagepath.open("ab") as f:
                            f.write(data)
        return imagepath.relative_to(settings.STATIC_ROOT)

    @property
    def clip(self):
        imagepath = Path(settings.STATIC_ROOT) / f"cropped/{self.lst_result_id}.jpg"
        imagepath.parent.mkdir(parents=True, exist_ok=True)
        if not imagepath.exists():
            image = Image.open(settings.STATIC_ROOT / self.local_image())
            # calculate coordinates and dimensions of annotated area:
            height, width = image.size
            left = int(self.data["x"]/100 * height)
            upper = int(self.data["y"]/100 * width)
            crop_width = int(self.data["width"]/100 * height)
            crop_height = int(self.data["height"]/100 * width)
            # store the area in crop and make a thumbnail out of it
            dims = (left, upper, left+crop_width, upper+crop_height)
            crop = image.crop(dims)
            crop.thumbnail((800, 800))
            crop.save(imagepath)
        return imagepath.relative_to(settings.STATIC_ROOT)


auditlog.register(Person, serialize_data=True)
auditlog.register(Place, serialize_data=True)
auditlog.register(Institution, serialize_data=True)
auditlog.register(AddressData, serialize_data=True)


class TimespanMixin(models.Model):
    from_date = FuzzyDateParserField(blank=True, null=True)
    to_date = FuzzyDateParserField(blank=True, null=True)

    class Meta:
        abstract = True


class NsvisRelationMixin:
    pass


class CollaboratesWith(NsvisRelationMixin, Relation):
    subj_model = Person
    obj_model = Person


class IsMemberOf(TimespanMixin, NsvisRelationMixin, Relation):
    subj_model = Person
    obj_model = Institution

    @classmethod
    def name(self) -> str:
        return _("is member of")

    @classmethod
    def reverse_name(self) -> str:
        return _("has as member")


class IsInventoriedIn(NsvisRelationMixin, Relation):
    subj_model = Person
    obj_model = Institution
    contact = models.CharField(blank=True, default="", max_length=4096)
    extent = models.CharField(blank=True, default="", max_length=4096)

    @classmethod
    def name(self) -> str:
        return _("is inventoried in")

    @classmethod
    def reverse_name(self) -> str:
        return _("inventories")


class IsLearningAt(TimespanMixin, NsvisRelationMixin, Relation):
    subj_model = Person
    obj_model = EducationType

    details = models.CharField(blank=True, default="", max_length=4096, verbose_name=_("Details"))

    @classmethod
    def name(self) -> str:
        return _("is learning at")

    @classmethod
    def reverse_name(self) -> str:
        return _("has as student")


class WorksAs(TimespanMixin, NsvisRelationMixin, Relation):
    subj_model = Person
    obj_model = ProfessionType

    details = models.CharField(blank=True, default="", max_length=4096, verbose_name=_("Details"))

    @classmethod
    def name(self) -> str:
        return _("is working as")

    @classmethod
    def reverse_name(self) -> str:
        return _("practiced by")


class LivesIn(TimespanMixin, NsvisRelationMixin, Relation):
    subj_model = Person
    obj_model = [Place, AddressData]

    @classmethod
    def name(self) -> str:
        return _("lives in")

    @classmethod
    def reverse_name(self) -> str:
        return _("has habitant")


class HasStudioIn(TimespanMixin, NsvisRelationMixin, Relation):
    subj_model = Person
    obj_model = [Place, AddressData]

    @classmethod
    def name(self) -> str:
        return _("has studio in")

    @classmethod
    def reverse_name(self) -> str:
        return _("is address for studio of")


class AddressInPlace(NsvisRelationMixin, Relation):
    subj_model = AddressData
    obj_model = Place


class BornIn(Relation):
    subj_model = Person
    obj_model = Place

    @classmethod
    def name(self) -> str:
        return _("born in")

    @classmethod
    def reverse_name(self) -> str:
        return _("is birth place of")


class DiedIn(NsvisRelationMixin, Relation):
    subj_model = Person
    obj_model = Place

    @classmethod
    def name(self) -> str:
        return _("died in")

    @classmethod
    def reverse_name(self) -> str:
        return _("is place of death of")


class ExileIn(TimespanMixin, NsvisRelationMixin, Relation):
    subj_model = Person
    obj_model = Place

    @classmethod
    def name(self) -> str:
        return _("was in exile in")

    @classmethod
    def reverse_name(self) -> str:
        return _("was place of exile for")


auditlog.register(CollaboratesWith)
auditlog.register(IsMemberOf)
auditlog.register(IsInventoriedIn)
auditlog.register(IsLearningAt)
auditlog.register(LivesIn)
auditlog.register(AddressInPlace)
