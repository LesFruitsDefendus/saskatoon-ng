from django import template
from rest_framework.utils.urls import remove_query_param, replace_query_param
from saskatoon.pagination import BasicPageNumberPagination
from typing import List

register = template.Library()
page_query_param = BasicPageNumberPagination.page_query_param
page_size_query_param = BasicPageNumberPagination.page_size_query_param


@register.filter
def add_page_size_param(url: str) -> str:
    """adds page_size query parameter to the full request url"""
    try:
        url = _clean_url(url)
        url_has_params: bool = "?" in url

        if url_has_params:
            return "{}&page_size=".format(url)
        else:
            return "{}?page_size=".format(url)
    except Exception:
        return url


def _clean_url(url: str) -> str:
    """Removes the page and page_size query parameters"""
    url = remove_query_param(url, page_query_param)
    url = remove_query_param(url, page_size_query_param)
    return url


@register.filter
def get_pages_range(page_number: int) -> List[int]:
    """Returns a list containing numbers leading to the page_number param"""
    try:
        return [i for i in range(1, page_number+1)]
    except Exception:
        return [page_number]


@register.simple_tag
def get_page_url(url: str, page_number: int) -> str:
    """Replaces the page number query parameter of the url"""
    try:
        return replace_query_param(url, page_query_param, page_number)
    except Exception:
        return '#'
