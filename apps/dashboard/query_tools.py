from django.db.models import Count, Func, F, Value, CharField
from django.db.models.functions import Trunc
from rest_framework import serializers


def custom_format_time_stamp(self, range_name='day'):
    mapper = {
        'hour': "DD-MM-YY HH",
        'day': "DD Mon YYYY",
        'week': "IW  YYYY",
        'month': "Mon YYYY",
        'year': "YYYY",

    }
    return Func(
        F('normal_date'),
        Value(mapper[range_name]),
        function='to_char',
        output_field=CharField()
    )


def create_graph_query(queryset, timestamp_field_name, graph_range):
    validate_graph_range_option(graph_range, raise_exception=True)
    qs = queryset.annotate(normal_date=Trunc(expression=timestamp_field_name, kind=graph_range)).values(
        'normal_date').annotate(
        available=Count('id')).values('available', created_at=custom_format_time_stamp(graph_range)).order_by(
        'normal_date')
    return qs


VALID_GRAPH_RANGE = ['day', 'month', 'year', 'week', 'hour']


def validate_graph_range_option(option, raise_exception):
    if str(option).lower() in VALID_GRAPH_RANGE:
        return True
    if raise_exception:
        raise serializers.ValidationError(
            {'range': f"{option} is invalid choice valid choice  are : {VALID_GRAPH_RANGE}"})
    return False
