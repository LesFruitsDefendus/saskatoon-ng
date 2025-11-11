from collections import OrderedDict
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class BasicPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 200

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ('count', self.page.paginator.count),
                    ('next', self.get_next_link()),
                    ('previous', self.get_previous_link()),
                    ('pages_count', self.page.paginator.num_pages),
                    ('current_page_number', self.page.number),
                    ('items_per_page', self.page.paginator.per_page),
                    ('results', data),
                ]
            )
        )
