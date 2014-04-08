from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template

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

mockProject = {
    'title':"Swearing in Response to Pain",
    'faculty':"Science and Engineering",
    'role':"Data Manager",
    'spaceUsed':"26.7",
    'spaceMax':"50.0",
    'create':"14/4/2014",
    'update':"14/4/2014"
}

members = [
    {'title':"Josh", 'details':"Project Manager"},
    {'title':"Brad", 'details':"Admin"},
    {'title':"Millie", 'details':"Lead InvestiGAYtor"},
    {'title':"Adam", 'details':"Researcher"}
]

history = [
    {'title':"Member Added", 'details':"Millie was added to project"},
    {'title':"Database updated", 'details':"Data added to DB"},
    {'title':"Report approved", 'details':"Report approvedby Josh"},
    {'title':"Space Request denied", 'details':"Your request was denied by Josh"}
]



def home(request):
    t = get_template('test.html')
    html = t.render(Context({'user': request.user}))
    return HttpResponse(html)

def dashboard(request):
    t = get_template('dashboard.html')
    html = t.render(Context({'user': request.user,
                             'notifications':mockNotications,
                             'faculties':mockFaculties,
                             'projects': mockProjects}))
    return HttpResponse(html)

def project(request):
    t = get_template('project.html')
    html = t.render(Context({'user': request.user,
                             'project': mockProject,
                             'members': members,
                             'history': history}))
    return HttpResponse(html)

def faculty(request):
    t = get_template('faculty.html')
    html = t.render(Context({'user': request.user,
                             'projects': mockProjects[:5],
                             'members': members}))
    return HttpResponse(html)
