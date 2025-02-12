from apis_core.relations.forms import RelationForm


class NsvisRelationMixinForm(RelationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields["collections"]
