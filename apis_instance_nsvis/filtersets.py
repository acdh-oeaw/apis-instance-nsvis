from django_filters import UnknownFieldBehavior
from apis_core.apis_entities.filtersets import AbstractEntityFilterSet


class AnnotationFilterSet(AbstractEntityFilterSet):
    class Meta(AbstractEntityFilterSet.Meta):
        unknown_field_behavior = UnknownFieldBehavior.IGNORE
