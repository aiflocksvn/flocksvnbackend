from django_filters import rest_framework as filters
from .models import CompanyPresent, CompanyPresentCategory


class CompanyPresentFilter(filters.FilterSet):
    # category = filters.ModelMultipleChoiceFilter(queryset=CompanyPresentCategory.objects.all(),
    #                                              field_name='company_category')

    category = filters.ModelMultipleChoiceFilter(field_name='company_category',
                                                 to_field_name='company_present_category',
                                                 # lookup_type='in',
                                                 queryset=CompanyPresentCategory.objects.all()
                                                 )

    # category = filters.CharFilter(method="filter_category", field_name='category')
    # product_category = filters.CharFilter(method="filter_category", field_name='category')
    # id = filters.NumberFilter(lookup_expr='exact')

    class Meta:
        model = CompanyPresent
        fields = {
            'company_category': ['in'],
        }
