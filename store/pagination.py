
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 5  # Itens por página
    page_size_query_param = 'page_size'  # Permite ao cliente definir o tamanho
    # max_page_size = 100  # Limite máximo permitido
