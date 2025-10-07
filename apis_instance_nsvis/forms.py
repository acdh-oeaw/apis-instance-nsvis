from apis_core.relations.forms import RelationForm
from django.forms import ModelForm
from apis_instance_nsvis.models import Annotation


class NsvisRelationMixinForm(RelationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields["collections"]


class NsvisImageAnnotationForm(ModelForm):
    class Meta:
        model = Annotation
        fields = "__all__"
