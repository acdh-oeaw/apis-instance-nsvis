from apis_core.generic.forms import GenericFilterSetForm
from apis_core.relations.forms import RelationForm


class NsvisRelationMixinForm(RelationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields["collections"]


class AnnotationFilterSetForm(GenericFilterSetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(self.fields["collections"].initial)
        if not self.fields["collections"].initial:
            self.fields["collections"].initial = ([36], )
