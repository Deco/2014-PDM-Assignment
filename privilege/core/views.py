# -*- coding: utf-8 -*-

import datetime
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from core.models import *
from core.forms import *
from django.forms.models import modelformset_factory
from django.views.generic import CreateView, UpdateView
from django.db.models import Sum

@login_required(login_url='/login')
def view_dashboard(request):
    context = {}
    template = 'dashboard.html'
    
    faculty_membership_qs = FacultyMembership.objects.filter(member=request.user)
    faculties_qs = Faculty.objects.filter(facultymembership__in=faculty_membership_qs).order_by("update_time")

    project_membership_qs = ProjectMembership.objects.filter(member=request.user)
    projects_qs = Project.objects.filter(projectmembership__in=project_membership_qs).order_by("update_time")
    
    faculty_set = set()
    for project_membership in project_membership_qs:
        faculty_set.add(project_membership.project.faculty)
    
    for faculty in faculties_qs:
        faculty_set.add(faculty)
    
    context['faculties'] = []
    for faculty in faculty_set:
        faculty_membership = faculty.get_membership(request.user)
        faculty_project_membership_qs = ProjectMembership.objects.filter(project__faculty=faculty, member=request.user)
        
        role_count_dict = {}
        for project_membership in faculty_project_membership_qs:
            role_count_dict[project_membership.get_role_nice()] = role_count_dict.get(project_membership.get_role_nice(), 0)+1
        
        role_list = [
            {'name': "Manager"               , 'count': faculty_membership and faculty_membership.role == FacultyMembership.MANAGER  and -1 or 0},
            {'name': "Approver"              , 'count': faculty_membership and faculty_membership.role == FacultyMembership.APPROVER and -1 or 0},
            {'name': "Principal Investigator", 'count': role_count_dict.get("Principal Investigator", 0)},
            {'name': "Data Manager"          , 'count': role_count_dict.get("Data Manager"          , 0)},
            {'name': "Collaborator"          , 'count': role_count_dict.get("Collaborator"          , 0)},
            {'name': "Researcher"            , 'count': role_count_dict.get("Researcher"            , 0)},
        ]
        
        context['faculties'].append({
            'id': faculty.id,
            'name': faculty.name,
            'role_list': role_list,
        })
    
    context['projects'] = []
    for project in projects_qs:
        membership = project.get_membership(request.user)
        context['projects'].append({
            'id': project.id,
            'title': project.title,
            'faculty': project.faculty,
            'storage_capacity_mb': project.storage_capacity_mb,
            'storage_used_mb': project.storage_used_mb,
            'creation_time': project.creation_time,
            'update_time': project.update_time,
            
            'user_role': membership and membership.get_role_nice() or 'blah',
        })
    
    return render(request, template, context)

@login_required(login_url='/login')
def view_faculty_list(request):
    # need to filter by permissions here
    faculties = Faculty.objects.all().order_by("name")
    context = {}
    template = 'faculty_list.html'
    
    context['faculties'] = faculties
    
    return render(request, template, context)

@login_required(login_url='/login')
def view_faculty_info(request, id=None):
    template = "faculty_info.html"
    context = {}
    
    try:
        faculty = Faculty.objects.get(pk=id)
    except Faculty.DoesNotExist:
        return view_error(request, "Faculty with ID {} does not exist.".format(id))
    
    context['faculty_name'] = faculty.name
    context['faculty_update_time'] = faculty.update_time
    context['faculty_creation_time'] = faculty.creation_time
    context['faculty_members'] = []
    for faculty_member in faculty.members.all().order_by("last_name"):
        membership = faculty.get_membership(faculty_member)
        context['faculty_members'].append({
            'user': faculty_member,
            'role': membership and membership.get_role_nice() or "—"
        })
    context['faculty_storage_used_mb'] = Project.objects.filter(faculty=faculty).aggregate(Sum('storage_used_mb'))['storage_used_mb__sum']
    context['faculty_storage_claimed_mb'] = Project.objects.filter(faculty=faculty).aggregate(Sum('storage_capacity_mb'))['storage_capacity_mb__sum']
    
    if context['faculty_storage_claimed_mb'] > 0:
        context['faculty_storage_used_percent'] = int(100*context['faculty_storage_used_mb']/context['faculty_storage_claimed_mb'])
        context['faculty_storage_free_percent'] = 100-int(100*context['faculty_storage_used_mb']/context['faculty_storage_claimed_mb'])
    else:
        context['faculty_storage_used_percent'] = 0
        context['faculty_storage_free_percent'] = 100
    
    try:
        membership = FacultyMembership.objects.get(faculty=faculty, member=request.user)
        context['faculty_user_role'] = dict(FacultyMembership.FACULTY_ROLES).get(membership.role, 'unknown')
    except FacultyMembership.DoesNotExist:
        membership = None
        context['faculty_user_role'] = "—"
    
    if membership and membership.role == "M":
        
        formset = modelformset_factory(
                FacultyMembership,
                form=FacultyMembershipForm,
                extra=5
            )
            
        if request.method == "GET":
            formset = formset(queryset=faculty.facultymembership_set.all())
            context['faculty_membership_formset'] = formset
            
        if request.method == "POST":
            formset = formset(request.POST, queryset=faculty.facultymembership_set.all())
            
            if formset.is_valid():
                formset.save()
            
        context['faculty_membership_formset'] = formset  
    
    return render(request, template, context)

@login_required(login_url='/login')
def view_faculty_delete(request, id=None):
    pass

@login_required(login_url='/login')
def view_faculty_create_project(request, id=None):
    pass

@login_required(login_url='/login')
def view_project_list(request):
    # need to filter by permissions here
    projects = Project.objects.all().order_by("title")
    context = {}
    template = 'project_list.html'
    
    context['projects'] = projects
    
    return render(request, template, context)

@login_required(login_url='/login')
def view_project_info(request, id=None):
    form_method = (request.method == "POST" and request.POST or None)
    template = 'project_info.html'
    context = {}
    #objects_tosave_list = []
    post_is_valid = False
    
    project = None
    faculty = None
    pd = {
        'project_membership' :None,
        'faculty_membership' :None,
        'can_edit': False,
        'can_delete': False,
    }
    
    try:
        project = Project.objects.get(id=id)
    except Project.DoesNotExist:
        return view_error(request, "Project with ID {} does not exist.".format(id))
    
    faculty = project.faculty
    
    def fillpermissions():
        pd['project_membership'] = project.get_membership(request.user)
        context['project_user_role'] = (
                pd['project_membership'] and pd['project_membership'].get_role_nice()
            or  "—"
        )
        pd['faculty_membership'] = faculty.get_membership(request.user)
        
        pd['can_edit'] = (
                pd['project_membership'] and (
                        pd['project_membership'].role == ProjectMembership.PRINCIPALINVESTIGATOR
                    or  pd['project_membership'].role == ProjectMembership.DATAMANAGER
                )
            or  pd['faculty_membership'] and (
                    pd['faculty_membership'].role == FacultyMembership.MANAGER
                )
        )
        pd['can_delete'] = pd['faculty_membership'] and (pd['faculty_membership'].role == FacultyMembership.MANAGER)
        context['can_edit'] = pd['can_edit']
        context['can_delete'] = pd['can_delete']
    
    fillpermissions()
    
    membership_qs = ProjectMembership.objects.filter(project=project).order_by("member__last_name")
    
    form = ProjectForm(form_method, instance=project)
    context['form'] = form
    
    ProjectMembershipFormSet = modelformset_factory(ProjectMembership, form=ProjectMembershipForm, extra=5)
    membership_formset = ProjectMembershipFormSet(form_method, queryset=membership_qs)
    context['membership_formset'] = membership_formset
    
    for membership_form in membership_formset:
        membership_form.fields['role'].required = False
    
    if request.method == "POST":
        if not pd['can_edit']:
            return view_error(request, "You do not have permission to edit this project.")
        
        if form.is_valid() and membership_formset.is_valid():
            project = form.save(commit=False)
            project.save()
            if faculty != project.faculty:
                pass; pass; pass # todo: check permissions in other faculty (can we move to it?)
            
            faculty = project.faculty
            #objects_tosave_list.append(project)
            post_is_valid = True
            fillpermissions()
        else:
            context['project_form_bad'] = True
            context['edit_mode'] = True
    
    context['project_members'] = []
    membership_form_i = 0
    for membership_form in membership_formset.forms:
        membership = membership_form.instance
        member = (membership_form_i < membership_qs.count() and membership.member or None)
        
        if post_is_valid:
            if membership_form.has_changed():
                if membership_form.instance.pk and membership_form.cleaned_data['role'].strip() == '':
                    print("BEFORE: ", membership_qs.count())
                    membership_form.instance.delete()
                    print("AFTER: ", membership_qs.count())
                    membership_form_i += 1
                    continue
                
                membership = membership_form.save(commit=False)
                membership.project = project
                membership.save()
                #objects_tosave_list.append(membership)
        else:
            post_is_valid = False
        
        if member: 
            member_entry = {
                'id': member.id,
                'first_name': member.first_name,
                'last_name': member.last_name,
                'role':membership.get_role_nice(),
            }
        else:
            member_entry = {
                'is_addition': True,
            }
        
        member_entry['membership_form'] = membership_form
        context['project_members'].append(member_entry)
        membership_form_i += 1
    
    if request.method == "POST" and post_is_valid:
        #for object in objects_tosave_list:
        #    object.save()
        context['project_form_commited'] = True
    
    context['project_id'] = project.id
    context['project_title'] = project.title
    context['project_faculty_id'] = project.faculty.id
    context['project_faculty_name'] = project.faculty.name
    context['project_creation_time'] = project.creation_time
    context['project_update_time'] = project.update_time
    
    context['project_storage_used_mb'] = project.storage_used_mb
    context['project_storage_capacity_mb'] = project.storage_capacity_mb
    if project.storage_capacity_mb > 0:
        context['project_storage_used_percent'] = int(100*project.storage_used_mb/project.storage_capacity_mb)
        context['project_storage_free_percent'] = 100-int(100*project.storage_used_mb/project.storage_capacity_mb)
    else:
        context['project_storage_used_percent'] = 0
        context['project_storage_free_percent'] = 100
    
    return render(request, template, context)

@login_required(login_url='/login')
def view_project_delete(request, id=None):
    pass

@login_required(login_url='/login')
def view_project_create_request(request, id=None):
    #objects_tosave_list = []
    post_is_valid = False
    
    try:
        project = Project.objects.get(id=id)
    except Project.DoesNotExist:
        return view_error(request, "Project with ID {} does not exist.".format(id))
    
    try:
        membership = ProjectMembership.objects.get(project=project, member=request.user, role=ProjectMembership.DATAMANAGER)
    except ProjectMembership.DoesNotExist:
        return view_error(request, "You must be a 'Data Manager' for this project to create a request (project_id: {})".format(id))
    
    spacerequest = SpaceRequest()
    spacerequest.project      = project
    spacerequest.size_mb      = 512
    spacerequest.comment      = None
    spacerequest.status       = SpaceRequest.STATUS_INACTIVE
    spacerequest.request_time = None
    spacerequest.requested_by = request.user
    spacerequest.action_time  = None
    spacerequest.actioned_by  = None
    spacerequest.save()
    
    print(spacerequest.id)
    
    return redirect('/request/{}'.format(spacerequest.id))

@login_required(login_url='/login')
def view_request_list(request, id=None):
    pass

@login_required(login_url='/login')
def view_request_info(request, id=None):
    form_method = (request.method == "POST" and request.POST or None)
    template = 'request_info.html'
    context = {}
    
    try:
        spacerequest = SpaceRequest.objects.get(id=id)
    except SpaceRequest.DoesNotExist:
        return view_error(request, "Space request with ID {} does not exist.".format(id))
    
    project = spacerequest.project
    
    try:
        project_membership = ProjectMembership.objects.get(
            project=project, member=request.user
        )
    except ProjectMembership.DoesNotExist:
        project_membership = None
    
    try:
        faculty_membership = FacultyMembership.objects.get(
            faculty=project.faculty, member=request.user
        )
    except FacultyMembership.DoesNotExist:
        faculty_membership = None
    
    can_edit = (
            spacerequest.status == SpaceRequest.STATUS_INACTIVE
        and project_membership and (
                    project_membership.role == ProjectMembership.PRINCIPALINVESTIGATOR
                or  project_membership.role == ProjectMembership.DATAMANAGER
            )
    )
    can_activate = can_edit
    can_action = (
            spacerequest.status == SpaceRequest.STATUS_PENDING
        and faculty_membership and (
                    faculty_membership.role == FacultyMembership.MANAGER
                or  faculty_membership.role == FacultyMembership.APPROVER
            )
    )
    
    context['can_edit'] = can_edit
    context['can_activate'] = can_activate
    context['can_action'] = can_action
    context['can_delete'] = faculty_membership and (faculty_membership.role == FacultyMembership.MANAGER)
    
    form = SpaceRequestForm(form_method, instance=spacerequest)
    context['form'] = form
    
    if request.method == "POST":
        if form.is_valid():
            spacerequest = form.save(commit=False)
            if project != spacerequest.project:
                return view_error(request, "project change ??!?!?")
            
            spacerequest.save()
            context['spacerequest_form_commited'] = True
        else:
            context['spacerequest_form_bad'] = True
            context['edit_mode'] = True
    
    context['spacerequest_id'] = spacerequest.id
    context['spacerequest_size_mb'] = spacerequest.size_mb
    context['spacerequest_status'] = spacerequest.get_status_nice()
    context['spacerequest_request_time'] = spacerequest.request_time
    context['spacerequest_requested_by'] = spacerequest.requested_by
    context['spacerequest_action_time'] = spacerequest.action_time
    context['spacerequest_actioned_by'] = spacerequest.actioned_by
    
    context['project_id'] = project.id
    context['project_title'] = project.title
    context['project_faculty_id'] = project.faculty.id
    context['project_faculty_name'] = project.faculty.name
    
    if project_membership:
        context['project_user_role'] = project_membership.get_role_nice()
    else:
        context['project_user_role'] = "—"
    
    context['project_storage_used_mb'] = project.storage_used_mb
    context['project_storage_capacity_mb'] = project.storage_capacity_mb
    
    return render(request, template, context)

@login_required(login_url='/login')
def view_request_activate(request, id=None):
    try:
        spacerequest = SpaceRequest.objects.get(id=id)
    except SpaceRequest.DoesNotExist:
        return view_error(request, "Space request with ID {} does not exist.".format(id))
    
    try:
        project_membership = ProjectMembership.objects.get(
            project=spacerequest.project, member=request.user
        )
    except ProjectMembership.DoesNotExist:
        project_membership = None
    
    has_access = project_membership and (
            project_membership.role == ProjectMembership.PRINCIPALINVESTIGATOR
        or  project_membership.role == ProjectMembership.DATAMANAGER
    )
    if not has_access:
        return view_error(request, "You must be a 'Principal Investigator' or 'Data Manager' to activate a space request.")
    
    if not spacerequest.status == SpaceRequest.STATUS_INACTIVE:
        return view_error(request, "A request must be 'Inactive' to be activated.")
    
    spacerequest.request_time = datetime.datetime.now()
    spacerequest.requested_by = request.user
    spacerequest.status = SpaceRequest.STATUS_PENDING
    spacerequest.save()
    
    return redirect('/request/{}'.format(id))

@login_required(login_url='/login')
def view_request_approve(request, id=None):
    try:
        spacerequest = SpaceRequest.objects.get(id=id)
    except SpaceRequest.DoesNotExist:
        return view_error(request, "Space request with ID {} does not exist.".format(id))
    
    try:
        faculty_membership = FacultyMembership.objects.get(
            faculty=spacerequest.project.faculty, member=request.user,
        )
    except FacultyMembership.DoesNotExist:
        faculty_membership = None
    
    has_access = faculty_membership and (
            faculty_membership.role == FacultyMembership.MANAGER
        or  faculty_membership.role == FacultyMembership.APPROVER
    )
    
    if not has_access:
        return view_error(request, "You must be a 'Manager' or an 'Approver' for this faculty to approve a request (request_id: {})".format(id))
    
    if not spacerequest.status == SpaceRequest.STATUS_PENDING:
        return view_error(request, "A request must be 'Pending' to be approved.")
    
    project = spacerequest.project
    project.storage_capacity_mb = project.storage_capacity_mb+spacerequest.size_mb
    project.update_time = datetime.datetime.now()
    project.save()
    
    spacerequest.action_time = datetime.datetime.now()
    spacerequest.actioned_by = request.user
    spacerequest.status = SpaceRequest.STATUS_APPROVED
    spacerequest.save()
    
    return redirect('/request/{}'.format(id))

@login_required(login_url='/login')
def view_request_reject(request, id=None):
    try:
        spacerequest = SpaceRequest.objects.get(id=id)
    except SpaceRequest.DoesNotExist:
        return view_error(request, "Space request with ID {} does not exist.".format(id))
    
    try:
        faculty_membership = FacultyMembership.objects.get(
            faculty=spacerequest.project.faculty, member=request.user,
        )
    except FacultyMembership.DoesNotExist:
        faculty_membership = None
    
    has_access = faculty_membership and (
            faculty_membership.role == FacultyMembership.MANAGER
        or  faculty_membership.role == FacultyMembership.APPROVER
    )
    
    if not has_access:
        return view_error(request, "You must be a 'Manager' or an 'Approver' for this faculty to reject a request (request_id: {})".format(id))
    
    if not spacerequest.status == SpaceRequest.STATUS_PENDING:
        return view_error(request, "A request must be 'Pending' to be rejected.")
    
    spacerequest.action_time = datetime.datetime.now()
    spacerequest.actioned_by = request.user
    spacerequest.status = SpaceRequest.STATUS_REJECTED
    spacerequest.save()
    
    return redirect('/request/{}'.format(id))

@login_required(login_url='/login')
def view_request_delete(request, id=None):
    pass

@login_required(login_url='/login')
def view_user_info(request, id=None):
    pass

@login_required(login_url='/login')
def view_history(request, id=None):
    pass

def view_error(request, error_msg):
    context = {}
    template = 'error.html'
    
    context['message'] = error_msg
    
    return render(request, template, context)

