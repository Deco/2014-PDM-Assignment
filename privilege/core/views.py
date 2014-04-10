from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required

mockNotications = [
    {'title':"Request Approved - More Space", 'details':"Project: Color Blindness in Computing"},
    {'title':"Member Added - Dee Doss", 'details':"Project: Swearing as a Respose to Pain"},
    {'title':"Member Added - Brad Schoone", 'details':"Project: 272 Days and 1.5m"},
    {'title':"Database Updated", 'details':"Project: Color Blindness in Computing"},
    {'title':"Request Denied - New Project", 'details':"Project: Determining the Ballmer Peak"},
    {'title':"Member Removed - Geoff", 'details':"Project: Effects of cocaine on honey bees"},
    {'title':"Request Approved - More Space", 'details':"Swearing as a Response to Pain"},
    {'title':"Request Approved - New Project", 'details':"Project: Lorem ipsum - When to use Filler"},
    {'title':"Member Added - Geoff", 'details':"Projects: Effects of cocaine on honey bees"},
]

mockFaculties = [
    {'name':"Science and Engineering", 'role':"Approver, Data Manager(2)", 'update':"14/04/2014", 'spaceUsed':"1024", 'spaceMax':"2048", 'memberCount':"6"},
    {'name':"Department of Computing", 'role':"Principle Investigator (4)", 'update':"22/02/2012", 'spaceUsed':"2080", 'spaceMax':"4000", 'memberCount':"50"},
    {'name':"Arts", 'role':"Administrator, Principle Investigator(9)", 'update':"05/02/2014", 'spaceUsed':"1024", 'spaceMax':"2048", 'memberCount':"10"},
    {'name':"Law and Order", 'role':"None", 'update':"14/4/2014", 'spaceUsed':"1024", 'spaceMax':"2048", 'memberCount':"12"},
    {'name':"Medicine", 'role':"None", 'update':"14/4/2014", 'spaceUsed':"250", 'spaceMax':"500", 'memberCount':"16"},
    {'name':"Psychology", 'role':"None", 'update':"14/4/2014", 'spaceUsed':"99", 'spaceMax':"288", 'memberCount':"4"},
    {'name':"Architecture", 'role':"None", 'update':"14/4/2014", 'spaceUsed':"104", 'spaceMax':"148", 'memberCount':"5"},
    {'name':"Health Science", 'role':"None", 'update':"14/4/2014", 'spaceUsed':"90", 'spaceMax':"204", 'memberCount':"17"},
    {'name':"Business", 'role':"None", 'update':"14/4/2014", 'spaceUsed':"4", 'spaceMax':"100", 'memberCount':"2"}
]

mockProjects = [
    {'title':"Color Blindness in Computing", 'details':"School of Accounting", 'faculty':"Arts", 'spaceUsed':"20", 'spaceMax':"50", 'update':"14/4/2014", 'role':"Contributer", 'memberCount':"6", 'create':"01/01/1970"},
    {'title':"Effects of cocaine on honey bees", 'details':"Department of Science and Engineering", 'faculty':"Department of Science and Engineering", 'spaceUsed':"4", 'spaceMax':"16", 'update':"28/04/2013", 'role':"Lead Investigator", 'memberCount':"3", 'create':"01/01/1970"},
    {'title':"Swearing as a Response to Pain", 'details':"Department of Computing", 'faculty':"Department of Computing", 'spaceUsed':"99", 'spaceMax':"100", 'update':"20/04/1420", 'role':"Administrator", 'memberCount':"25", 'create':"01/01/1970"},
    {'title':"A Litterary Analysis of \"Bitches ain't shit\"", 'details':"Arts", 'faculty':"Arts", 'spaceUsed':"1", 'spaceMax':"2", 'update':"09/02/2012", 'role':"Contributer", 'memberCount':"9", 'create':"01/01/1970"},
    {'title':"272 Days and 1.5m", 'details':"Reddit", 'faculty':"Department of Computing", 'spaceUsed':"272", 'spaceMax':"365", 'update':"10/4/2014", 'role':"Lead Investigator", 'memberCount':"1.5", 'create':"01/01/1970"},
    {'title':"Mockito - To Kill a Mocking Class", 'details':"Department of Computing", 'faculty':"ArtsDepartment of Computing", 'spaceUsed':"2", 'spaceMax':"12", 'update':"14/09/2013", 'role':"Contributer", 'memberCount':"6", 'create':"01/01/1970"},
    {'title':"Using OpenStack for Great Good", 'details':"Department of Computing", 'faculty':"Department of Computing", 'spaceUsed':"29", 'spaceMax':"45", 'update':"01/04/2014", 'role':"Contributer", 'memberCount':"6", 'create':"01/01/1970"}
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
    {'title':"Millie", 'details':"Lead Investigator"},
    {'title':"Adam", 'details':"Researcher"}
]

history = [
    {'title':"Member Added", 'details':"Millie was added to project"},
    {'title':"Database updated", 'details':"Data added to DB"},
    {'title':"Report approved", 'details':"Report approvedby Josh"},
    {'title':"Space Request denied", 'details':"Your request was denied by Josh"}
]

mockFaculty = {
    'name':"Science and Engineering",
    'spaceUsed':"25",
    'spaceMax':"60",
    'roles':"Approver, Principal Inverigator(3), Data Manager (1), Contributer(6)",
    'create':"14/4/2014"
}



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

@login_required(login_url='/login/')
def project(request):
    t = get_template('project.html')
    html = t.render(Context({'user': request.user,
                             'project': mockProject,
                             'members': members,
                             'history': history}))
    return HttpResponse(html)

@login_required(login_url='/login/')
def faculty(request):
    t = get_template('faculty.html')
    html = t.render(Context({'user': request.user,
                             'projects': mockProjects[:5],
                             'members': members,
                             'faculty': mockFaculty}))
    return HttpResponse(html)

@login_required(login_url='/login/')
def projectList(request):
    t = get_template('projectList.html')
    html = t.render(Context({'user': request.user,
                             'projects': mockProjects,
                             'count': len(mockProjects)}))
    return HttpResponse(html)

@login_required(login_url='/login/')
def facultyList(request):
    t = get_template('facultyList.html')
    html = t.render(Context({'user': request.user,
                             'faculties': mockFaculties,
                             'count': len(mockFaculties)}))
    return HttpResponse(html)
