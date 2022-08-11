from django.conf import settings
from django.core.paginator import Paginator


def paginator(request, posts):
    paginator = Paginator(posts, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
