from rest_framework.pagination import PageNumberPagination


class EnlargedResultsSetPagination(PageNumberPagination):
    page_size = 40
