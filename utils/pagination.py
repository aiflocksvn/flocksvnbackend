from django.core.paginator import InvalidPage
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class Paginator(PageNumberPagination):
    page_size = 5
    page_query_param = 'page'
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        try:
            next_page = self.page.next_page_number()
        except InvalidPage:
            next_page = None
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            # 'nextPageNumber': next_page,
            'results': data
        })
