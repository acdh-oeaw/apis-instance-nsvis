import json
import uuid
from apis_core.relations.forms import RelationForm
from django import forms
from apis_instance_nsvis.models import Annotation
from apis_core.generic.forms import GenericModelForm
from django.forms.widgets import Input
from django_json_editor_field.widgets import JSONEditorWidget


class NsvisRelationMixinForm(RelationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields["collections"]


class CommaSeparatedListWidget(Input):
    input_type = "text"
    template_name = "widgets/multiline.html"

    class Media:
        js = ["js/multiline.js"]

    def value_from_datadict(self, data, files, name):
        ret = [item for item in data.getlist(name) if item]
        return json.dumps(ret)

    def format_value(self, value):
        return value


depicted_choices = [
    ("Einzelperson", "Einzelperson"),
    ("Frau", "Frau"),
    ("Mann", "Mann"),
    ("Kind", "Kind"),
    ("Personengruppe", "Personengruppe"),
    ("Architektur", "Architektur"),
    ("Interieur", "Interieur"),
    ("Objekt", "Objekt"),
    ("Tier", "Tier"),
    ("Natur", "Natur"),
    ("Landschaft- und Stadtansicht", "Landschaft- und Stadtansicht"),
    ("Landkarte", "Landkarte"),
    (
        "Reproduktion Kunstwerk Manuskript etc.",
        "Reproduktion Kunstwerk Manuskript etc.",
    ),
]

topic_choices = [
    ("Politik", "Politik"),
    ("Soziales", "Soziales"),
    ("Wohnen", "Wohnen"),
    ("Militär", "Militär"),
    ("Krieg", "Krieg"),
    ("Theater", "Theater"),
    ("Musik", "Musik"),
    ("Bildende Kunst", "Bildende Kunst"),
    ("Film", "Film"),
    ("Technik/Wissenschaft/Wirtschaft", "Technik/Wissenschaft/Wirtschaft"),
    ("Arbeit", "Arbeit"),
    ("Reise", "Reise"),
    ("Freizeit Feste Familie", "Freizeit Feste Familie"),
    ("Sport", "Sport"),
    ("Brauchtum", "Brauchtum"),
    ("Mode", "Mode"),
    ("Tanz", "Tanz"),
]

photographers_schema = {
    "title": "Photographers",
    "type": "array",
    "format": "table",
    "items": {
        "type": "object",
        "properties": {
            "agency": {
                "type": "string",
                "options": {
                    "inputAttributes": {
                        "placeholder": "Agency",
                    }
                },
            },
            "photographer": {
                "type": "string",
                "options": {
                    "inputAttributes": {
                        "placeholder": "Photographer",
                    }
                },
            },
        },
    },
}
photographers_options = {
    "schema": photographers_schema,
    "theme": "bootstrap5",
    "disable_collapse": True,
    "disable_edit_json": True,
    "disable_properties": True,
    "disable_array_reorder": True,
    "disable_array_delete_last_row": True,
    "disable_array_delete_all_rows": True,
    "prompt_before_delete": False,
}

photographers_help_text = (
    "Photographers ist eine Liste von 'Agentur` / 'Fotograf' Zuordnungen"
)


class AnnotationForm(GenericModelForm):
    author = forms.CharField(
        widget=CommaSeparatedListWidget(attrs={"class": "mb-1"}), required=False
    )
    lst_task_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    lst_annotation_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    lst_result_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    data = forms.JSONField(
        widget=forms.HiddenInput(attrs={"class": "input-data"}), required=True
    )
    depicted = forms.MultipleChoiceField(choices=depicted_choices)
    topic = forms.MultipleChoiceField(choices=topic_choices)
    photographers = forms.CharField(
        widget=JSONEditorWidget(options=photographers_options),
        required=False,
        help_text=photographers_help_text,
    )

    class Meta:
        model = Annotation
        fields = "__all__"
        widgets = {
            "caption": forms.Textarea(attrs={"rows": 3}),
            "title": forms.Textarea(attrs={"rows": 3}),
            "location": forms.Textarea(attrs={"rows": 3}),
            "other": forms.Textarea(attrs={"rows": 3}),
            "internal_comment": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.image = kwargs.pop("image", None)
        super().__init__(*args, **kwargs)
        if instance := kwargs.get("instance"):
            self.fields["lst_task_id"].initial = instance.lst_task_id
            self.fields["lst_annotation_id"].initial = instance.lst_annotation_id
            self.fields["lst_result_id"].initial = instance.lst_result_id
            self.fields["data"].initial = instance.data
            self.fields["photographers"].initial = json.dumps(instance.photographers)

    def save(self, *args, **kwargs):
        self.instance.image = self.instance.image or self.image
        self.instance.lst_task_id = self.instance.lst_task_id or -1
        self.instance.lst_annotation_id = self.instance.lst_annotation_id or -1
        self.instance.lst_result_id = self.instance.lst_result_id or uuid.uuid4()
        self.instance.data = self.instance.data or self.cleaned_data["data"]
        self.instance.photographers = json.loads(self.cleaned_data["photographers"])
        return super().save(*args, **kwargs)
