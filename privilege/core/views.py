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
from django.db.models import Q

@login_required(login_url='/login')
def view_dashboard(request):
    context = {}
    template = 'dashboard.html'
    
    faculty_membership_qs = FacultyMembership.objects.filter(member=request.user)
    faculties_qs = Faculty.objects.filter(facultymembership__in=faculty_membership_qs).order_by("update_time")

    project_membership_qs = ProjectMembership.objects.filter(member=request.user)
    projects_qs = Project.objects.filter(projectmembership__in=project_membership_qs).order_by("update_time")
    
    context['faculties'] = []
    for faculty in faculties_qs:
        faculty_membership = faculty.get_membership(request.user)
        faculty_project_membership_qs = ProjectMembership.objects.filter(project__faculty=faculty, member=request.user)
        
        role_count_dict = {}
        for project_membership in faculty_project_membership_qs:
            role_count_dict[project_membership.get_role_nice()] = (role_count_dict[project_membership.get_role_nice()] or 0)+1
        
        role_list = {
            {'name': "Manager"               , 'count': faculty_membership and faculty_membership.role == FacultyMembership.MANAGER  and -1 or 0},
            {'name': "Approver"              , 'count': faculty_membership and faculty_membership.role == FacultyMembership.APPROVER and -1 or 0},
            {'name': "Principal Investigator", 'count': role_count_dict["Principal Investigator"] or 0},
            {'name': "Data Manager"          , 'count': role_count_dict["Data Manager"]           or 0},
            {'name': "Collaborator"          , 'count': role_count_dict["Collaborator"]           or 0},
            {'name': "Researcher"            , 'count': role_count_dict["Researcher"]             or 0},
        }
        
        context['faculties'].append({
            'name': faculty.name,
            'role_list': role_list,
        })
    
    context['projects'] = []
    for project in projects_qs:
        membership = project.get_membership(request.user)
        context['projects'].append({
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
    faculty = Faculty.objects.get(pk=id)
    template = "faculty_info.html"
    context = {'faculty': faculty}
    
    
    FacultyMe
    if Faculty
    
    
    
    return render(request, template, context)
    
    

@login_required(login_url='/login')
def view_faculty_form(request, id=None):
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
    # need to filter by permissions here
    try:
        project = Project.objects.get(id=id)
    except Project.DoesNotExist:
        return view_error(request, "Project with ID {} does not exist.".format(id))
    
    context = {}
    template = 'project_info.html'
    
    context['project'] = project
    context['project_members'] = []
    for projectMember in project.members.all().order_by("last_name"):
        membership = project.get_membership(projectMember)
        context['project_members'].append({
            'user': projectMember,
            'role': membership and membership.get_role_nice() or "—"
        })
    
    if project.storage_capacity_mb > 0:
        context['project_storage_used_percent'] = int(100*project.storage_used_mb/project.storage_capacity_mb)
        context['project_storage_free_percent'] = 100-int(100*project.storage_used_mb/project.storage_capacity_mb)
    else:
        context['project_storage_used_percent'] = 0
        context['project_storage_free_percent'] = 100
    
    try:
        membership = ProjectMembership.objects.get(project=project, member=request.user)
        context['project_user_role'] = dict(ProjectMembership.PROJECT_ROLES).get(membership.role, 'unknown')
    except ProjectMembership.DoesNotExist:
        context['project_user_role'] = "—"
    
    return render(request, template, context)

@login_required(login_url='/login')
def view_project_form(request, id=None):
    template = "project_form.html"
    
    if id:
        proj = Project.objects.get(pk=id)
        is_new = False
    else:
        proj = None
        is_new = True
    
    
    if request.method == "GET":
        form = ProjectForm(instance=proj)
        formset = modelformset_factory(ProjectMembership, form=ProjectMembershipForm, extra=5)
        
        projMembership = ProjectMembership.objects.filter(project=proj).order_by('id')
        formset = formset(queryset=projMembership)
        
        return render(request, template, {'form': form, 'formset': formset, 'is_new': is_new})
        
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=proj)
        formset = modelformset_factory(ProjectMembership, form=ProjectMembershipForm, extra=5)
        projMembership = ProjectMembership.objects.filter(project=proj).order_by('id')
        formset = formset(request.POST, queryset=projMembership)
        
        if form.is_valid() and formset.is_valid():
            project = form.save(commit=False)
            project.save()
            
            for form in formset.forms:
                if form.has_changed():
                    projMembership = form.save(commit=False)
                    projMembership.project = project
                    projMembership.save()
            
            return redirect('/project/{}'.format(project.id))
            
        else:
            return render(request, template, {'form': form, 'formset': formset, 'is_new': is_new})

@login_required(login_url='/login')

def view_user_info(request, id=None):
    pass

@login_required(login_url='/login')
def view_request_list(request, id=None):
    pass

@login_required(login_url='/login')
def view_request_info(request, id=None):
    pass

@login_required(login_url='/login')
def view_request_form(request, id=None, project_id=None):
    template = "request_form.html"
    formClass = RequestForm
    user = request.user
    instance = None
    project = None
    is_new = True
    
    if id:
        instance = SpaceRequest.objects.get(pk=id)
        is_new = False
        
    if project_id:
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return view_error(request, "Project ID is invalid (project_id: {}).".format(project_id))
        
        try:
            membership = ProjectMembership.objects.get(project=project, member=user, role=ProjectMembership.DATAMANAGER)
        except ProjectMembership.DoesNotExist:
            return view_error(request, "You must be a 'Data Manager' for this project to create a request (project_id: {})".format(project_id))
    
    if request.method == "GET":
        form = formClass(user, instance=instance, initial={'project':project.id})
        return render(request, template, {'form': form, 'is_new': is_new})
        
    if request.method == "POST":
        from django.contrib import auth
        form = formClass(user, instance=instance)
        
        if form.is_valid():
            instance = form.save(commit=False)
            instance.requested_by = request.user
            instance.date_requested = datetime.datetime.now()
            instance.save()
            
            return redirect('/project/{}'.format(project.id))
            
        else:
            return render(request, template, {'form': form, 'is_new': is_new})

@login_required(login_url='/login')
def view_history(request, id=None):
    pass

def view_error(request, error_msg):
    context = {}
    template = 'error.html'
    
    context['message'] = error_msg
    
    return render(request, template, context)




