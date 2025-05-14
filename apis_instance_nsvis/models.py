import logging
from urllib.parse import urlparse
from pathlib import Path
from PIL import Image
import httpx

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import slugify
from apis_core.apis_entities.abc import E53_Place, SimpleLabelModel, E21_Person
from apis_core.history.models import VersionMixin
from apis_core.apis_entities.models import AbstractEntity
from apis_core.relations.models import Relation
from apis_core.generic.abc import GenericModel
from django.contrib.postgres.fields import ArrayField
from django_interval.fields import FuzzyDateParserField
from django_json_editor_field.fields import JSONEditorField
from apis_instance_nsvis.utils import S3, MyImgProxy, customdateparser

from auditlog.registry import auditlog

logger = logging.getLogger(__name__)

s3 = S3()


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


class SpecialArea(GenericModel, VersionMixin, MongoDbDataMixin, SimpleLabelModel):
    class Meta(SimpleLabelModel.Meta):
        verbose_name = _("Special Area")
        verbose_name_plural = _("Special Areas")


class Person(AbstractEntity, VersionMixin, MongoDbDataMixin, E21_Person):
    _default_search_fields = ["forename", "surname"]

    class Meta(E21_Person.Meta):
        ...

    class GenderChoices(models.TextChoices):
        MALE = "male", _("male")
        FEMALE = "female", _("female")

    # we override inherited fields to either disable or adapt them
    gender = models.CharField(blank=True, choices=GenderChoices, default="", max_length=4096, verbose_name=_("Gender"))
    date_of_birth = None
    date_of_death = None

    # custom fields:
    citizenship = models.CharField(blank=True, default="", max_length=4096, verbose_name=_("Citizenship"))
    address_comment = models.TextField(blank=True, default="", verbose_name=_("Address Comment"))
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
    work_ban = models.CharField(max_length=8, choices=Choices, default=Choices.UNK, verbose_name=_("Work ban during NS"))
    work_ns = models.CharField(max_length=9, choices=Choices, default=Choices.UNK, verbose_name=_("Worked during NS"))
    propaganda_membership = models.CharField(max_length=9, choices=Choices, default=Choices.UNK, verbose_name=_("Member in a propaganda company"))

    def __str__(self):
        return f"{self.forename} {self.surname}"


class Place(E53_Place, AbstractEntity, VersionMixin, MongoDbDataMixin):
    @classmethod
    def create_from_string(cls, string):
        return cls.objects.create(label=string)


class Institution(AbstractEntity, VersionMixin, MongoDbDataMixin):
    """ Zeitschriften, Verlage, Agenturen, Partei + Vorfeldorganisation """
    class Meta:
        verbose_name = _("Institution")
        verbose_name_plural = _("Institutions")

    label = models.CharField(blank=True, default="", max_length=4096, verbose_name=_("Label"))

    def __str__(self):
        return self.label

    @classmethod
    def create_from_string(cls, string):
        return cls.objects.create(label=string)


class EducationType(AbstractEntity, VersionMixin, MongoDbDataMixin, SimpleLabelModel):
    class Meta(SimpleLabelModel.Meta):
        verbose_name = _("Education Type")
        verbose_name_plural = _("Education Types")


class ProfessionType(AbstractEntity, VersionMixin, MongoDbDataMixin, SimpleLabelModel):
    class Meta(SimpleLabelModel.Meta):
        verbose_name = _("Profession Type")
        verbose_name_plural = _("Profession Types")


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
        verbose_name = _("annotation")
        verbose_name_plural = _("annotations")

    def __str__(self):
        if label := self.data.get("iiif_label"):
            return f"{self.issue} ({label}) [{self.lst_result_id}]"
        return self.issue

    @property
    def pagepath(self):
        suffix = Path(urlparse(self.image).path).suffix
        issueslug = slugify(self.issue)
        imagepath = f"23503/{issueslug}/{self.lst_result_id}{suffix}"
        return imagepath

    @property
    def page(self):
        headers = {'Origin': "https://label-studio.acdh-dev.oeaw.ac.at"}
        tmp = Path("/tmp") / self.pagepath
        if not tmp.exists():
            tmp.parent.mkdir(parents=True, exist_ok=True)
            with httpx.stream("GET", self.image, headers=headers) as r:
                if r.status_code == httpx.codes.OK:
                    for data in r.iter_bytes():
                        with tmp.open("ab") as f:
                            f.write(data)
        return tmp

    def local_image(self):
        if not s3.file_exists(self.pagepath):
            logger.info("Downloading and uploading file to s3: %s", self.page)
            s3.upload_file(self.page, self.pagepath)
        myimgproxy = MyImgProxy()
        return myimgproxy.calc(self.pagepath)

    @property
    def clip(self):
        imagepath = f"23503/cropped/{self.lst_result_id}.jpg"
        if not s3.file_exists(imagepath):
            tmp = Path("/tmp") / imagepath
            tmp.parent.mkdir(parents=True, exist_ok=True)
            image = Image.open(self.page)
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
            crop.save(tmp)
            s3.upload_file(tmp, imagepath)
        myimgproxy = MyImgProxy()
        return myimgproxy.calc(imagepath)


auditlog.register(SpecialArea, serialize_data=True)
auditlog.register(Person, serialize_data=True)
auditlog.register(Place, serialize_data=True)
auditlog.register(Institution, serialize_data=True)
auditlog.register(EducationType, serialize_data=True)
auditlog.register(ProfessionType, serialize_data=True)


class TimespanMixin(models.Model):
    from_date = FuzzyDateParserField(blank=True, null=True, parser=customdateparser)
    to_date = FuzzyDateParserField(blank=True, null=True, parser=customdateparser)

    class Meta:
        abstract = True


class NsvisRelationMixin:
    class Meta:
        ordering = ["pk"]


class CollaboratesWith(NsvisRelationMixin, TimespanMixin, Relation):
    subj_model = Person
    obj_model = Person

    @classmethod
    def name(self) -> str:
        return _("collaborates with")

    @classmethod
    def reverse_name(self) -> str:
        return _("collaborates with")


class IsMemberOf(NsvisRelationMixin, TimespanMixin, Relation):
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


class IsLearningAt(NsvisRelationMixin, TimespanMixin, Relation):
    subj_model = Person
    obj_model = EducationType

    details = models.CharField(blank=True, default="", max_length=4096, verbose_name=_("Details"))

    @classmethod
    def name(self) -> str:
        return _("is learning at")

    @classmethod
    def reverse_name(self) -> str:
        return _("has as student")


class WorksAs(NsvisRelationMixin, TimespanMixin, Relation):
    subj_model = Person
    obj_model = ProfessionType

    details = models.CharField(blank=True, default="", max_length=4096, verbose_name=_("Details"))

    @classmethod
    def name(self) -> str:
        return _("is working as")

    @classmethod
    def reverse_name(self) -> str:
        return _("practiced by")


class LivesIn(NsvisRelationMixin, TimespanMixin, Relation):
    subj_model = Person
    obj_model = Place

    @classmethod
    def name(self) -> str:
        return _("lives in")

    @classmethod
    def reverse_name(self) -> str:
        return _("has habitant")


class HasStudioIn(NsvisRelationMixin, TimespanMixin, Relation):
    subj_model = Person
    obj_model = Place

    @classmethod
    def name(self) -> str:
        return _("has studio in")

    @classmethod
    def reverse_name(self) -> str:
        return _("is address for studio of")


class LocatedIn(NsvisRelationMixin, Relation):
    subj_model = Place
    obj_model = Place

    @classmethod
    def name(self) -> str:
        return _("located in")

    @classmethod
    def reverse_name(self) -> str:
        return _("is location of")


class BornIn(NsvisRelationMixin, Relation):
    subj_model = Person
    obj_model = Place
    date = FuzzyDateParserField(blank=True, null=True, parser=customdateparser)

    @classmethod
    def name(self) -> str:
        return _("born in")

    @classmethod
    def reverse_name(self) -> str:
        return _("is birth place of")


class DiedIn(NsvisRelationMixin, Relation):
    subj_model = Person
    obj_model = Place
    date = FuzzyDateParserField(blank=True, null=True, parser=customdateparser)

    @classmethod
    def name(self) -> str:
        return _("died in")

    @classmethod
    def reverse_name(self) -> str:
        return _("is place of death of")


class ExileIn(NsvisRelationMixin, TimespanMixin, Relation):
    subj_model = Person
    obj_model = Place

    @classmethod
    def name(self) -> str:
        return _("was in exile in")

    @classmethod
    def reverse_name(self) -> str:
        return _("was place of exile for")


class ImprisonedIn(NsvisRelationMixin, TimespanMixin, Relation):
    subj_model = Person
    obj_model = Place

    @classmethod
    def name(self) -> str:
        return _("is imprisoned in")

    @classmethod
    def reverse_name(self) -> str:
        return _("is place of imprisonment for")


class IsInheritanceIn(NsvisRelationMixin, Relation):
    subj_model = Person
    obj_model = Institution

    @classmethod
    def name(self) -> str:
        return _("is inheritance in")

    @classmethod
    def reverse_name(self) -> str:
        return _("contains inheritance of")


auditlog.register(CollaboratesWith)
auditlog.register(IsMemberOf)
auditlog.register(IsInventoriedIn)
auditlog.register(IsLearningAt)
auditlog.register(WorksAs)
auditlog.register(LivesIn)
auditlog.register(HasStudioIn)
auditlog.register(LocatedIn)
auditlog.register(BornIn)
auditlog.register(DiedIn)
auditlog.register(ExileIn)
auditlog.register(ImprisonedIn)
auditlog.register(IsInheritanceIn)
