import json
from django import template
from django.contrib.contenttypes.models import ContentType
from apis_core.relations.templatetags.relations import relations_from
from apis_core.generic.helpers import first_member_match, module_paths
from apis_core.relations.tables import RelationsListTable

register = template.Library()


@register.filter
def pretty_json(value):
    return json.dumps(value, indent=2)


@register.simple_tag
def relation_types_by_string_list(relation_types):
    relation_types = relation_types.split(",")
    relation_types = [relation_type.split(".") for relation_type in relation_types]
    relation_types = [ContentType.objects.get(app_label=relation[0].strip(), model=relation[1].strip()) for relation in relation_types]
    return relation_types


@register.simple_tag(takes_context=True)
def relations_instances_from_relation_types(context, relation_types):
    relations = []

    for relation_type in relation_types:
        relations.extend(relations_from(context["object"], relation_type))

    return relations


@register.simple_tag(takes_context=True)
def custom_relations_list_table(context, relations, suffix=""):
    suffix = f"{suffix}RelationsTable"
    table_modules = tuple(module_paths(type(context["object"]), path="tables", suffix=suffix))
    table_class = first_member_match(table_modules, RelationsListTable)
    return table_class(relations, request=context["request"])
