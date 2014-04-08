from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required

mockNotications = [
    {'title':"Request Approved - more space", 'details':"Project: Color Blindness in Computing"},
    {'title':"Member Added - Dee Doss", 'details':"Project: Swearing as a respose to pain"},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."}
]

mockFaculties = [
    {'title':"Science and Engineering", 'details':"Approver, Data Manager(2)"},
    {'title':"Department of Computing", 'details':"Principal Investigator (4)"},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."}
]

mockProjects = [
    {'title':"Color Blindness in Computing", 'details':"School of Accounting"},
    {'title':"Effects of cocaine on honey bees", 'details':"Department of Science and Engineering"},
    {'title':"Swearing as a Response to Pain", 'details':"Department of Computing"},
    {'title':"A Litterary Analysis of \"Bitches ain't shit\"", 'details':"Arts"},
    {'title':"272 Days and 1.5m", 'details':"Computing Department"},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."},
    {'title':"Filler", 'details':"Lorem ipsum dolor sit amet."}
]

def home(request):
    t = get_template('test.html')
    html = t.render(Context({'user': request.user}))
    return HttpResponse(html)

@login_required(login_url='/login/')
def dashboard(request):
    t = get_template('dashboard.html')
    html = t.render(Context({'user': request.user,
                             'notifications':mockNotications,
                             'faculties':mockFaculties,
                             'projects': mockProjects}))
    return HttpResponse(html)
