from datetime import date
import django_tables2 as tables
from apis_core.apis_entities.tables import AbstractEntityTable
from apis_core.relations.tables import RelationsListTable


class AnnotationTable(AbstractEntityTable):
    issue = tables.TemplateColumn(template_code="<a href={{ record.get_absolute_url }}>{{ record.issue }}</a>")
    labelstudio = tables.TemplateColumn(template_name="columns/labelstudio_link.html", exclude_from_export=True)
    topic = tables.TemplateColumn(template_code="{{ record.topic|join:', ' }}")
    depicted = tables.TemplateColumn(template_code="{{ record.depicted|join:', ' }}")
    clip = tables.TemplateColumn(template_code="<img class='thumbnail' src={{ record.clip }}>", exclude_from_export=True)

    class Meta(AbstractEntityTable.Meta):
        exclude = ["desc"]
        fields = ["caption"]


class DatesColumn(tables.TemplateColumn):
    template_name = "apis_instance_nsvis/columns/dates.html"

    def __init__(self, *args, **kwargs):
        super().__init__(template_name=self.template_name, *args, **kwargs)


class TimespanTable(RelationsListTable):
    dates = DatesColumn()

    class Meta(RelationsListTable.Meta):
        sequence = (list(RelationsListTable.Meta.sequence)[:-3] + ["dates"] + list(RelationsListTable.Meta.sequence)[-3:])

    def sort(self):
        def sort_date(val):
            d1 = getattr(val, "date_date_sort", None)
            d2 = getattr(val, "from_date_date_sort", None)
            d3 = getattr(val, "to_date_date_sort", None)
            return d1 or d2 or d3 or date.today()
        self.rows.data = sorted(self.rows.data, key=sort_date)

    def __init__(self, *args, **kwargs):
        kwargs["orderable"] = False
        kwargs["show_header"] = False
        super().__init__(*args, **kwargs)
        self.sort()

    def paginate(self, *args, **kwargs):
        self.sort()
        super().paginate(*args, **kwargs)


class PersonInventoryRelationsTable(TimespanTable):
    class Meta(TimespanTable.Meta):
        ...


class PersonOrganizationRelationsTable(TimespanTable):
    class Meta(TimespanTable.Meta):
        ...


class PersonCareerRelationsTable(TimespanTable):
    details = tables.Column()

    class Meta(TimespanTable.Meta):
        sequence = (list(TimespanTable.Meta.sequence)[:-4] + ["details"] + list(TimespanTable.Meta.sequence)[-4:])


class PersonPlacesRelationsTable(TimespanTable):
    class Meta(TimespanTable.Meta):
        ...
