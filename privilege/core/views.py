from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template


def home(request):
    t = get_template('test.html')
    html = t.render(Context({'user': request.user}))
    return HttpResponse(html)


