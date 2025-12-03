from datetime import date
import django_tables2 as tables
from apis_core.generic.tables import GenericTable
from apis_core.relations.tables import RelationsListTable
from apis_instance_nsvis.models import Annotation


class AnnotationTable(GenericTable):
    issue = tables.TemplateColumn(template_code="<a href={{ record.get_absolute_url }}>{{ record.issue }}</a>")
    labelstudio = tables.TemplateColumn(template_name="columns/labelstudio_link.html", exclude_from_export=True)
    topic = tables.TemplateColumn(template_code="{{ record.topic|join:', ' }}")
    depicted = tables.TemplateColumn(template_code="{{ record.depicted|join:', ' }}")
    clip = tables.TemplateColumn(template_code="<img class='thumbnail' src={{ record.clip }}>", exclude_from_export=True)
    author = tables.TemplateColumn(template_name="columns/annotation_author.html")
    photographers = tables.TemplateColumn(template_name="columns/annotation_photographers.html")
    ranking = tables.TemplateColumn(template_code='<abbr title="{{ record.ranking }}">{{ record.ranking|floatformat:-3 }}</abbr>')
    caption = tables.Column(attrs={"td": {"class": "col-1"}})

    class Meta(GenericTable.Meta):
        exclude = ["desc", "id"]
        attrs = {"class": "table table-sm", "style": "font-size: 14px"}


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


class AbstractEntityInventoryRelationsTable(TimespanTable):
    extent = tables.Column()
    contact = tables.Column()

    class Meta(TimespanTable.Meta):
        ...


class AbstractEntityOrganizationRelationsTable(TimespanTable):
    details = tables.Column()

    class Meta(TimespanTable.Meta):
        ...


class AbstractEntityCareerRelationsTable(TimespanTable):
    details = tables.Column()

    class Meta(TimespanTable.Meta):
        sequence = (list(TimespanTable.Meta.sequence)[:-4] + ["details"] + list(TimespanTable.Meta.sequence)[-4:])


class AbstractEntityPlacesRelationsTable(TimespanTable):
    class Meta(TimespanTable.Meta):
        ...
