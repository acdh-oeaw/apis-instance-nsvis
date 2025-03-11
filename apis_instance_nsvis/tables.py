import django_tables2 as tables
from apis_core.apis_entities.tables import AbstractEntityTable
from apis_core.relations.tables import RelationsListTable


class AnnotationTable(AbstractEntityTable):
    issue = tables.TemplateColumn(template_code="<a href={{ record.get_absolute_url }}>{{ record.issue }}</a>")
    labelstudio = tables.TemplateColumn(template_name="columns/labelstudio_link.html")
    topic = tables.TemplateColumn(template_code="{{ record.topic|join:', ' }}")
    depicted = tables.TemplateColumn(template_code="{{ record.depicted|join:', ' }}")
    clip = tables.TemplateColumn(template_code="{% load static %}<img class='thumbnail' src={% static record.clip %}>")

    class Meta(AbstractEntityTable.Meta):
        exclude = ["desc"]
        fields = ["caption"]


class TimespanTable(RelationsListTable):
    from_date = tables.TemplateColumn(order_by="from_date_date_sort", template_code="<abbr title='{{ record.from_date_date_sort }}'>{{ record.from_date }}</abbr>")
    to_date = tables.Column(order_by="to_date_sort")

    class Meta(RelationsListTable.Meta):
        sequence = (list(RelationsListTable.Meta.sequence)[:-3] + ["from_date", "to_date"] + list(RelationsListTable.Meta.sequence)[-3:])
        order_by = ("from_date",)


class PersonInventoryRelationsTable(TimespanTable):
    class Meta(TimespanTable.Meta):
        ...


class PersonOrganizationRelationsTable(TimespanTable):
    class Meta(TimespanTable.Meta):
        ...


class PersonCareerRelationsTable(TimespanTable):
    details = tables.Column()

    class Meta(TimespanTable.Meta):
        sequence = (list(TimespanTable.Meta.sequence)[:-5] + ["details"] + list(TimespanTable.Meta.sequence)[-5:])


class PersonPlacesRelationsTable(TimespanTable):
    date = tables.Column(order_by="date")

    class Meta(TimespanTable.Meta):
        sequence = (list(RelationsListTable.Meta.sequence)[:-3] + ["date", "from_date", "to_date"] + list(RelationsListTable.Meta.sequence)[-3:])
