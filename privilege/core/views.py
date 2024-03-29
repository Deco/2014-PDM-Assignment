# -*- coding: utf-8 -*-

import datetime
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from core.models import *
from core.forms import *
from core.history import *
from django.forms.models import modelformset_factory
from django.views.generic import CreateView, UpdateView
from django.db.models import Sum, Q
import core.comments

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
            {'name': "Faculty Manager"       , 'count': faculty_membership and faculty_membership.role == FacultyMembership.MANAGER  and -1 or 0},
            {'name': "Faculty Approver"      , 'count': faculty_membership and faculty_membership.role == FacultyMembership.APPROVER and -1 or 0},
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
            'faculty_id': project.faculty.id,
            'faculty_name': project.faculty.name,
            'storage_capacity_mb': project.storage_capacity_mb,
            'storage_used_mb': project.storage_used_mb,
            'creation_time': project.creation_time,
            'update_time': project.update_time,
            
            'user_role': membership and membership.get_role_nice() or 'blah',
        })
    
    context['historyevents'] = find_history(
        HistoryEntry.objects.filter(
                Q(referenced_project__in=projects_qs)
            |   Q(referenced_faculty__in=faculties_qs)
            |   Q(referenced_user_primary =request.user)
            |   Q(referenced_user_secondary=request.user)
        ).order_by("-occurence_time")[:50],
        None
    )
    
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
    form_method = (request.method == "POST" and request.POST or None)
    template = 'faculty_info.html'
    context = {}
    post_is_valid = False
    
    faculty = None
    pd = {
        'membership' :None,
        'can_edit': False,
        'can_delete': False,
    }
    
    try:
        faculty = Faculty.objects.get(id=id)
    except Faculty.DoesNotExist:
        return view_error(request, "Faculty with ID {} does not exist.".format(id))
    
    def fillpermissions():
        pd['membership'] = faculty.get_membership(request.user)
        context['faculty_user_role'] = (
                pd['membership'] and pd['membership'].get_role_nice()
            or  "—"
        )
        
        pd['can_edit'] = pd['membership'] and (
            pd['membership'].role == FacultyMembership.MANAGER
        )
        pd['can_delete'] = pd['can_edit']
        context['can_edit'] = pd['can_edit']
        context['can_delete'] = pd['can_delete']
    
    fillpermissions()
    
    project_qs = Project.objects.filter(faculty=faculty).order_by("-update_time")
    spacerequest_qs = SpaceRequest.objects.filter(project__faculty=faculty).order_by("-update_time")
    membership_qs = FacultyMembership.objects.filter(faculty=faculty).order_by("member__last_name")
    
    faculty_curr_name = faculty.name
    
    form = FacultyForm(form_method, instance=faculty)
    context['form'] = form
    
    FacultyMembershipFormSet = modelformset_factory(FacultyMembership, form=FacultyMembershipForm, extra=5)
    membership_formset = FacultyMembershipFormSet(form_method, queryset=membership_qs)
    context['membership_formset'] = membership_formset
    
    for membership_form in membership_formset:
        membership_form.fields['role'].required = False
    
    if request.method == "POST":
        if not pd['can_edit']:
            return view_error(request, "You do not have permission to edit this faculty.")
        
        if form.is_valid() and membership_formset.is_valid():
            faculty = form.save(commit=False)
            
            change_str_parts = ["Changes: "]
            if faculty_curr_name != faculty.name:
                change_str_parts.append('Name changed to "{0}";'.format(faculty.name))
            else:
                change_str_parts.append('None')
            change_str = ' '.join(change_str_parts)
            
            if form.has_changed():
                faculty.update_time = datetime.datetime.now()
                faculty.save()
                
                record_history(kind=HistoryEntry.FACULTY_EDITED,
                    note=change_str,
                    referenced_faculty=faculty,
                    referenced_user_primary=request.user
                )
            
            post_is_valid = True
            fillpermissions()
        else:
            context['faculty_form_bad'] = True
            context['edit_mode'] = True
    
    context['faculty_members'] = []
    membership_form_i = 0
    for membership_form in membership_formset.forms:
        membership = membership_form.instance
        member = (membership_form_i < membership_qs.count() and membership.member or None)
        
        if post_is_valid and membership_form.has_changed():
            if membership_form.instance.pk and membership_form.cleaned_data['role'].strip() == '':
                membership_form.instance.delete()
                
                record_history(kind=HistoryEntry.FACULTY_MEMBER_REMOVED,
                    note='User "{0}" removed.'.format(membership.member),
                    referenced_faculty=faculty,
                    referenced_user_primary=request.user,
                    referenced_user_secondary=membership_form.instance.member
                )
                
                membership_form_i += 1
                continue
            
            prev_role_str = (member and FacultyMembership.objects.get(id=membership.id).get_role_nice())
            
            membership = membership_form.save(commit=False)
            membership.faculty = faculty
            membership.save()
            
            record_history(kind=(member and HistoryEntry.FACULTY_MEMBER_CHANGED or HistoryEntry.FACULTY_MEMBER_ADDED),
                note=(
                        member and 'User "{0}" changed from "{1}" to "{2}".'.format(membership.member, prev_role_str, membership.get_role_nice())
                    or             'User "{0}" added as "{1}".'.format(membership.member, membership.get_role_nice())
                ),
                referenced_faculty=faculty,
                referenced_user_primary=request.user,
                referenced_user_secondary=membership.member
            )
        
        if member: 
            member_entry = {
                'id': member.id,
                'first_name': member.first_name,
                'last_name': member.last_name,
                'role': membership.get_role_nice(),
            }
        else:
            member_entry = {
                'is_addition': True,
            }
        
        member_entry['membership_form'] = membership_form
        context['faculty_members'].append(member_entry)
        membership_form_i += 1
    
    if request.method == "POST" and post_is_valid:
        context['faculty_form_commited'] = True
    
    context['faculty_id'] = faculty.id
    context['faculty_name'] = faculty.name
    context['faculty_creation_time'] = faculty.creation_time
    context['faculty_update_time'] = faculty.update_time
    
    context['faculty_storage_used_mb'] = project_qs.aggregate(Sum('storage_used_mb'))['storage_used_mb__sum']
    context['faculty_storage_capacity_mb'] = project_qs.aggregate(Sum('storage_capacity_mb'))['storage_capacity_mb__sum']
    context['faculty_storage_free_mb'] = context['faculty_storage_capacity_mb']-context['faculty_storage_used_mb']
    if context['faculty_storage_capacity_mb'] > 0:
        context['faculty_storage_used_percent'] = int(100*context['faculty_storage_used_mb']/context['faculty_storage_capacity_mb'])
        context['faculty_storage_free_percent'] = 100-int(100*context['faculty_storage_used_mb']/context['faculty_storage_capacity_mb'])
    else:
        context['faculty_storage_used_percent'] = 0
        context['faculty_storage_free_percent'] = 100
    
    context['faculty_projects'] = []
    for project in project_qs:
        membership = project.get_membership(request.user)
        context['faculty_projects'].append({
            'id': project.id,
            'title': project.title,
            'storage_capacity_mb': project.storage_capacity_mb,
            'storage_used_mb': project.storage_used_mb,
            'creation_time': project.creation_time,
            'update_time': project.update_time,
            
            'user_role': membership and membership.get_role_nice() or "—",
        })
    
    context['faculty_spacerequests'] = []
    context['faculty_spacerequests_pendingcount'] = 0
    context['faculty_spacerequests_approvedcount'] = 0
    context['faculty_spacerequests_rejectedcount'] = 0
    for spacerequest in spacerequest_qs:
        context['faculty_spacerequests'].append({
            'id': spacerequest.id,
            'size_mb': spacerequest.size_mb,
            'status': spacerequest.get_status_nice(),
            'requested_by': spacerequest.requested_by,
            'update_time': spacerequest.update_time,
            'project_title': spacerequest.project.title,
        })
        context['faculty_spacerequests_pendingcount' ] += (spacerequest.status == SpaceRequest.STATUS_PENDING  and 1 or 0)
        context['faculty_spacerequests_approvedcount'] += (spacerequest.status == SpaceRequest.STATUS_APPROVED and 1 or 0)
        context['faculty_spacerequests_rejectedcount'] += (spacerequest.status == SpaceRequest.STATUS_REJECTED and 1 or 0)
    
    project_membership_qs = ProjectMembership.objects.filter(project__faculty=faculty, member=request.user)
    
    role_count_dict = {}
    for project_membership in project_membership_qs:
        role_count_dict[project_membership.get_role_nice()] = role_count_dict.get(project_membership.get_role_nice(), 0)+1
    
    role_list = [
        {'name': "Manager"               , 'count': pd['membership'] and pd['membership'].role == FacultyMembership.MANAGER  and -1 or 0},
        {'name': "Approver"              , 'count': pd['membership'] and pd['membership'].role == FacultyMembership.APPROVER and -1 or 0},
        {'name': "Principal Investigator", 'count': role_count_dict.get("Principal Investigator", 0)},
        {'name': "Data Manager"          , 'count': role_count_dict.get("Data Manager"          , 0)},
        {'name': "Collaborator"          , 'count': role_count_dict.get("Collaborator"          , 0)},
        {'name': "Researcher"            , 'count': role_count_dict.get("Researcher"            , 0)},
    ]
    
    context['role_list'] = role_list
    
    context['faculty_historyevents'] = find_history(
        HistoryEntry.objects.filter(referenced_faculty=faculty).order_by("-occurence_time"),
        faculty
    )
    
    context['comment_object'] = faculty
    
    return render(request, template, context)

@login_required(login_url='/login')
def view_faculty_delete(request, id=None):
    return view_privilege(request)

@login_required(login_url='/login')
def view_faculty_create_project(request, id=None):
    try:
        faculty = Faculty.objects.get(id=id)
    except Faculty.DoesNotExist:
        return view_error(request, "Faculty with ID {} does not exist.".format(id))
    
    faculty_membership = faculty.get_membership(request.user)
    if not faculty_membership or faculty_membership.role != FacultyMembership.MANAGER:
        return view_error(request, 'You must be a "Faculty Manager" to create a project.')
    
    project = Project()
    project.title  = "Untitled project."
    project.faculty = faculty
    project.storage_capacity_mb = 1024
    project.storage_used_mb = 850
    project.creation_time = datetime.datetime.now()
    project.update_time = datetime.datetime.now()
    project.save()
    
    record_history(kind=HistoryEntry.PROJECT_CREATED,
        note='Project created in faculty "{0}"'.format(faculty.name),
        referenced_faculty=faculty,
        referenced_project=project,
        referenced_user_primary=request.user,
    )
    
    return redirect('/project/{}'.format(project.id))


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
        'project_membership': None,
        'faculty_membership': None,
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
        context['can_request'] = pd['project_membership'] and (
                pd['project_membership'].role == ProjectMembership.PRINCIPALINVESTIGATOR
            or  pd['project_membership'].role == ProjectMembership.DATAMANAGER
        )
    
    fillpermissions()
    
    spacerequest_qs = SpaceRequest.objects.filter(project=project).order_by("-update_time")
    membership_qs = ProjectMembership.objects.filter(project=project).order_by("member__last_name")
    
    project_curr_title = project.title
    project_curr_faculty = project.faculty
    
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
            
            change_str_parts = ["Changes: "]
            if project_curr_title != project.title:
                change_str_parts.append('Title changed to "{0}";'.format(project.title))
            if project_curr_faculty != project.faculty:
                change_str_parts.append('Faculty changed from "{0}" to "{1}";'.format(project_curr_faculty.id, project.faculty.id))
            if len(change_str_parts) == 1:
                change_str_parts.append('None')
            change_str = ' '.join(change_str_parts)
            
            if project_curr_faculty != project.faculty:
                pass; pass; pass # todo: check permissions in other faculty (can we move to it?)
            
            if form.has_changed():
                project.update_time = datetime.datetime.now()
                project.save()
                
                record_history(kind=HistoryEntry.PROJECT_EDITED,
                    note=change_str,
                    referenced_project=project,
                    referenced_user_primary=request.user,
                )
            
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
        
        if post_is_valid and membership_form.has_changed():
            if membership_form.instance.pk and membership_form.cleaned_data['role'].strip() == '':
                membership_form.instance.delete()
                
                record_history(kind=HistoryEntry.PROJECT_MEMBER_REMOVED,
                    note='User "{0}" removed.'.format(membership.member),
                    referenced_project=project,
                    referenced_user_primary=request.user,
                    referenced_user_secondary=membership_form.instance.member,
                )
                
                membership_form_i += 1
                continue
            
            prev_role_str = (member and ProjectMembership.objects.get(id=membership.id).get_role_nice())
            
            membership = membership_form.save(commit=False)
            membership.project = project
            membership.save()
            #objects_tosave_list.append(membership)
            
            record_history(kind=(member and HistoryEntry.PROJECT_MEMBER_CHANGED or HistoryEntry.PROJECT_MEMBER_ADDED),
                note=(
                        member and 'User "{0}" changed from "{1}" to "{2}".'.format(membership.member, prev_role_str, membership.get_role_nice())
                    or             'User "{0}" added as "{1}".'.format(membership.member, membership.get_role_nice())
                ),
                referenced_project=project,
                referenced_user_primary=request.user,
                referenced_user_secondary=membership.member,
            )
        
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
        fillpermissions()
    
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
    
    context['project_spacerequests'] = []
    for spacerequest in spacerequest_qs:
        context['project_spacerequests'].append({
            'id': spacerequest.id,
            'size_mb': spacerequest.size_mb,
            'status': spacerequest.get_status_nice(),
            'requested_by': spacerequest.requested_by,
            'update_time': project.update_time,
        })
    
    context['project_historyevents'] = find_history(
        HistoryEntry.objects.filter(referenced_project=project).order_by("-occurence_time"),
        project
    )
    
    context['comment_object'] = project
    
    return render(request, template, context)

@login_required(login_url='/login')
def view_project_delete(request, id=None):
    return view_privilege(request)

@login_required(login_url='/login')
def view_project_create_request(request, id=None):
    #objects_tosave_list = []
    post_is_valid = False
    
    try:
        project = Project.objects.get(id=id)
    except Project.DoesNotExist:
        return view_error(request, "Project with ID {} does not exist.".format(id))
    
    try:
        membership = ProjectMembership.objects.get(
            project=project, member=request.user,
            role__in=[ProjectMembership.DATAMANAGER, ProjectMembership.PRINCIPALINVESTIGATOR]
        )
    except ProjectMembership.DoesNotExist:
        return view_error(request, "You must be a 'Data Manager' or 'Principal Investigator' for this project to create a request (project_id: {})".format(id))
    
    spacerequest = SpaceRequest()
    spacerequest.project      = project
    spacerequest.size_mb      = 512
    spacerequest.comment      = None
    spacerequest.status       = SpaceRequest.STATUS_INACTIVE
    spacerequest.request_time = None
    spacerequest.requested_by = request.user
    spacerequest.action_time  = None
    spacerequest.actioned_by  = None
    spacerequest.update_time  = datetime.datetime.now()
    spacerequest.save()
    
    record_history(kind=HistoryEntry.SPACE_REQUEST_CREATED,
        note="Requested additional size: {0}MB".format(spacerequest.size_mb),
        referenced_request=spacerequest,
        #referenced_project=spacerequest.project,
        referenced_user_primary=request.user,
    )
    
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
    
    spacerequest_curr_size_mb = spacerequest.size_mb
    
    form = SpaceRequestForm(form_method, instance=spacerequest)
    context['form'] = form
    
    if request.method == "POST":
        if form.is_valid():
            spacerequest = form.save(commit=False)
            if project != spacerequest.project:
                return view_error(request, "project change ??!?!?")
            
            change_str_parts = ["Changes: "]
            if spacerequest_curr_size_mb != spacerequest.size_mb:
                change_str_parts.append('Requested size addition changed to {0}MB;'.format(spacerequest.size_mb))
            if len(change_str_parts) == 1:
                change_str_parts.append('None')
            change_str = ' '.join(change_str_parts)
            
            spacerequest.update_time  = datetime.datetime.now()
            spacerequest.save()
            
            record_history(kind=HistoryEntry.SPACE_REQUEST_EDITED,
                note=change_str,
                referenced_request=spacerequest,
                referenced_user_primary=request.user,
                email_qs=User.objects.filter(
                        Q(projectmembership__project=spacerequest.project        , projectmembership__role__in=[ProjectMembership.PRINCIPALINVESTIGATOR,ProjectMembership.DATAMANAGER])
                    |   Q(facultymembership__faculty=spacerequest.project.faculty, facultymembership__role__in=[FacultyMembership.MANAGER,FacultyMembership.APPROVER])
                ).distinct(),
                # User is a member of spacerequest.project with role in [PRINCIPALINVESTIGATOR, DATAMANAGER]
                # OR
                # User is a member of spacerequest.project.faculty with role in [MANAGER, APPROVER]
                
                #User.objects.filter(
                #    Q(that complicated thing) & ~Q(id=request.user.id)
                #)
            )
            
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
    
    context['spacerequest_historyevents'] = find_history(
        HistoryEntry.objects.filter(referenced_request=spacerequest).order_by("-occurence_time"),
        spacerequest
    )
    
    context['comment_object'] = spacerequest
    
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
    spacerequest.update_time  = datetime.datetime.now()
    spacerequest.save()
    
    record_history(kind=HistoryEntry.SPACE_REQUEST_ACTIVATED,
        note="Requested additional size: {0}MB".format(spacerequest.size_mb),
        referenced_request=spacerequest,
        referenced_project=spacerequest.project,
        referenced_user_primary=request.user,
    )
    
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
    spacerequest.update_time  = datetime.datetime.now()
    spacerequest.save()
    
    record_history(kind=HistoryEntry.SPACE_REQUEST_APPROVED,
        note="Additional size: {0}MB".format(spacerequest.size_mb),
        referenced_request=spacerequest,
        referenced_project=spacerequest.project,
        referenced_user_primary=request.user,
    )
    
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
    spacerequest.update_time  = datetime.datetime.now()
    spacerequest.save()
    
    record_history(kind=HistoryEntry.SPACE_REQUEST_REJECTED,
        note="Requested additional size: {0}MB".format(spacerequest.size_mb),
        referenced_request=spacerequest,
        referenced_project=spacerequest.project,
        referenced_user_primary=request.user,
    )
    
    return redirect('/request/{}'.format(id))

@login_required(login_url='/login')
def view_request_delete(request, id=None):
    return view_privilege(request)

@login_required(login_url='/login')
def view_user_info(request, id=None):
    template = 'user_info.html'
    context = {}
    
    user = None
    
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return view_error(request, "User with ID {} does not exist.".format(id))
    
    context['user_first_name'] = user.first_name
    context['user_last_name'] = user.last_name
    context['user_id'] = user.id
    context['user_date_joined'] = user.date_joined
    
    context['user_historyevents'] = find_history(
        HistoryEntry.objects.filter(
            Q(referenced_user_primary=user) | Q(referenced_user_secondary=user)
        ).order_by("-occurence_time"),
        user
    )
    
    project_membership_qs = ProjectMembership.objects.filter(member=user)
    project_qs = Project.objects.filter(projectmembership__in=project_membership_qs).order_by("update_time")
    
    context['user_projects'] = []
    for project in project_qs:
        membership = project.get_membership(user)
        context['user_projects'].append({
            'id': project.id,
            'title': project.title,
            'update_time': project.update_time,
            'faculty_id': project.faculty.id,
            'faculty_name': project.faculty.name,
            
            'user_role': membership and membership.get_role_nice() or "—",
        })
    
    faculty_membership_qs = FacultyMembership.objects.filter(member=user)
    faculty_qs = Faculty.objects.filter(facultymembership__in=faculty_membership_qs).order_by("update_time")
    
    context['user_faculties'] = []
    for faculty in faculty_qs:
        membership = faculty.get_membership(user)
        faculty_project_membership_qs = ProjectMembership.objects.filter(project__faculty=faculty, member=user)
        
        role_count_dict = {}
        for project_membership in faculty_project_membership_qs:
            role_count_dict[project_membership.get_role_nice()] = role_count_dict.get(project_membership.get_role_nice(), 0)+1
        
        role_list = [
            {'name': "Faculty Manager"       , 'count': membership and membership.role == FacultyMembership.MANAGER  and -1 or 0},
            {'name': "Faculty Approver"      , 'count': membership and membership.role == FacultyMembership.APPROVER and -1 or 0},
            {'name': "Principal Investigator", 'count': role_count_dict.get("Principal Investigator", 0)},
            {'name': "Data Manager"          , 'count': role_count_dict.get("Data Manager"          , 0)},
            {'name': "Collaborator"          , 'count': role_count_dict.get("Collaborator"          , 0)},
            {'name': "Researcher"            , 'count': role_count_dict.get("Researcher"            , 0)},
        ]
        
        context['user_faculties'].append({
            'id': faculty.id,
            'name': faculty.name,
            'update_time': faculty.update_time,
            'role_list': role_list
        })
    
    context['comment_object'] = user
    
    return render(request, template, context)

@login_required(login_url='/login')
def view_history(request, id=None):
    pass

def view_error(request, error_msg):
    context = {}
    template = 'error.html'
    
    context['message'] = error_msg
    
    return render(request, template, context)

def view_privilege(request):
    return render(request, 'privilege.html', {})

