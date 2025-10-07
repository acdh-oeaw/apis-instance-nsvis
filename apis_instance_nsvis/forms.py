import uuid
from apis_core.relations.forms import RelationForm
from django import forms
from apis_instance_nsvis.models import Annotation
from apis_core.generic.forms import GenericModelForm


class NsvisRelationMixinForm(RelationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields["collections"]


class NsvisImageAnnotationForm(GenericModelForm):
    lst_task_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    lst_annotation_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    lst_result_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    data = forms.JSONField(widget=forms.HiddenInput(attrs={"class": "input-data"}), required=True)

    class Meta:
        model = Annotation
        fields = "__all__"
        widgets = {
                "caption": forms.Textarea(attrs={'rows': 3}),
                "title": forms.Textarea(attrs={'rows': 3}),
                "location": forms.Textarea(attrs={'rows': 3}),
                "other": forms.Textarea(attrs={'rows': 3}),
                "internal_comment": forms.Textarea(attrs={'rows': 3}),
                }

    def __init__(self, *args, **kwargs):
        self.image = kwargs.pop("image")
        super().__init__(*args, **kwargs)
        if instance := kwargs.get("instance"):
            self.fields["lst_task_id"].initial = instance.lst_task_id
            self.fields["lst_annotation_id"].initial = instance.lst_annotation_id
            self.fields["lst_result_id"].initial = instance.lst_result_id
            self.fields["data"].initial = instance.data

    def save(self, *args, **kwargs):
        self.instance.image = self.instance.image or self.image
        self.instance.lst_task_id = self.instance.lst_task_id or -1
        self.instance.lst_annotation_id = self.instance.lst_annotation_id or -1
        self.instance.lst_result_id = self.instance.lst_result_id or uuid.uuid4()
        self.instance.data = self.instance.data or self.cleaned_data["data"]
        super().save(*args, **kwargs)
