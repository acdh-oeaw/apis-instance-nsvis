from datetime import datetime
import re
from django.db.models import Q
from django.forms.widgets import CheckboxInput
from django_filters import UnknownFieldBehavior, FilterSet, MultipleChoiceFilter, BooleanFilter, CharFilter
from apis_core.relations.filtersets import RelationFilterSet
from apis_core.apis_entities.filtersets import AbstractEntityFilterSet
from apis_instance_nsvis.models import Annotation
from django_interval.fields import FuzzyDateParserField
from django_interval.filters import YearIntervalRangeFilter


class TimespanMixinFilterSet(RelationFilterSet):
    class Meta(RelationFilterSet.Meta):
        unknown_field_behavior = UnknownFieldBehavior.IGNORE
        filter_overrides = {
                FuzzyDateParserField: {
                    'filter_class': YearIntervalRangeFilter
                }
        }


class BornInFilterSet(RelationFilterSet):
    class Meta(RelationFilterSet.Meta):
        unknown_field_behavior = UnknownFieldBehavior.IGNORE
        filter_overrides = {
                FuzzyDateParserField: {
                    'filter_class': YearIntervalRangeFilter
                }
        }


class DiedInFilterSet(RelationFilterSet):
    class Meta(RelationFilterSet.Meta):
        unknown_field_behavior = UnknownFieldBehavior.IGNORE
        filter_overrides = {
                FuzzyDateParserField: {
                    'filter_class': YearIntervalRangeFilter
                }
        }


class CustomMultipleChoiceFilter(MultipleChoiceFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra["choices"] = self.get_choices()

    def get_choices(self):
        choices = set()
        for value in Annotation.objects.exclude(Q(**{f"{self.field_name}__isnull": True})).values_list(self.field_name, flat=True):
            for val in value:
                choices.add(val)
        choices = sorted(choices)
        return list(zip(choices, choices))

    def filter(self, qs, value):
        q = Q()
        for val in value:
            q |= Q(**{f"{self.field_name}__contains": [val]})
        return qs.filter(q)


class IssueFilter(MultipleChoiceFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra["choices"] = self.get_choices()

    def _sortissue(self, issue):
        title, date = issue.split(" vom ")
        date = datetime.strptime(date, "%d.%m.%Y")
        return (title, date)

    def get_choices(self):
        issues = sorted(set(Annotation.objects.values_list(self.field_name, flat=True)), key = lambda x: self._sortissue(x))
        return list(zip(issues, issues))

    def filter(self, qs, value):
        q = Q()
        for val in value:
            q |= Q(**{f"{self.field_name}__contains": val})
        return qs.filter(q)


class IssueYearFilter(MultipleChoiceFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra["choices"] = self.get_choices()

    def get_choices(self):
        issues = sorted(Annotation.objects.values_list(self.field_name, flat=True))
        years = set()
        for issue in issues:
            if match := re.search("(?P<year>19\d\d)", issue):
                years.add(int(match["year"]))
        return list(zip(years, years))

    def filter(self, qs, value):
        q = Q()
        for val in value:
            q |= Q(**{f"{self.field_name}__contains": val})
        return qs.filter(q)


class MagazineFilter(IssueFilter):
    def get_choices(self):
        issues = sorted(Annotation.objects.values_list(self.field_name, flat=True).distinct())
        issues = [issue.split(" vom ") for issue in issues]
        issues = {issue[0] for issue in issues}
        return list(zip(issues, issues))


class InternalCommentExistsFilter(BooleanFilter):
    def filter(self, qs, value):
        if value:
            return qs.filter(internal_comment__isnull=not value)
        return qs


class MultipleAuthors(BooleanFilter):
    def filter(self, qs, value):
        if value:
            return qs.filter(author__len__gt=1)
        return qs


class AgencyFilter(MultipleChoiceFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra["choices"] = self.get_choices()

    def get_choices(self):
        photographers = Annotation.objects.values_list("photographers", flat=True)
        agencies = sorted({entry["agency"] for agency in photographers for entry in agency if entry["agency"]})
        return list(zip(agencies, agencies))

    def _json_list_contains_value(self, json_list, value):
        for item in json_list:
            for val in value:
                if item["agency"] == val:
                    return True
        return False

    def filter(self, qs, value):
        if value:
            annotations = Annotation.objects.values("photographers", "pk")
            annotation_ids = [annotation["pk"] for annotation in annotations if self._json_list_contains_value(annotation["photographers"], value)]
            return qs.filter(pk__in=annotation_ids)
        return qs


class PhotographerFilter(MultipleChoiceFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra["choices"] = self.get_choices()

    def get_choices(self):
        photographers = Annotation.objects.values_list("photographers", flat=True)
        photographers = sorted({entry["photographer"] for photographer in photographers for entry in photographer if entry["photographer"]})
        return list(zip(photographers, photographers))

    def _json_list_contains_value(self, json_list, value):
        for item in json_list:
            for val in value:
                if item["photographer"] == val:
                    return True
        return False

    def filter(self, qs, value):
        if value:
            annotations = Annotation.objects.values("photographers", "pk")
            annotation_ids = [annotation["pk"] for annotation in annotations if self._json_list_contains_value(annotation["photographers"], value)]
            return qs.filter(pk__in=annotation_ids)
        return qs


class AuthorContainsFilter(CharFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(lookup_expr="icontains", *args, **kwargs)

    def filter(self, qs, value):
        q = Q()
        for val in value.split():
            q |= Q(**{f"{self.field_name}__icontains": val})
        return qs.filter(q)


class AnnotationFilterSet(AbstractEntityFilterSet):
    author_contains = AuthorContainsFilter(field_name="author")

    class Meta(AbstractEntityFilterSet.Meta):
        unknown_field_behavior = UnknownFieldBehavior.IGNORE
        fields = {"caption": ["icontains"], "title": ["icontains", "exact"], "location": ["icontains"], "other": ["icontains"]}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["years"] = IssueYearFilter(field_name="issue")
        self.filters["issue"] = IssueFilter(field_name="issue")
        self.filters["magazine"] = MagazineFilter(field_name="issue")
        self.filters["author"] = CustomMultipleChoiceFilter(field_name="author")
        self.filters["topic"] = CustomMultipleChoiceFilter(field_name="topic")
        self.filters["depicted"] = CustomMultipleChoiceFilter(field_name="depicted")
        self.filters["internal_comment"] = InternalCommentExistsFilter(widget=CheckboxInput)
        self.filters["multiple_authors"] = MultipleAuthors(widget=CheckboxInput)
        self.filters["agency"] = AgencyFilter()
        self.filters["photographer"] = PhotographerFilter()
        del self.filters["changed_since"]
        del self.filters["relation"]
