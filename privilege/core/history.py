# -*- coding: utf-8 -*-
import datetime
from core.models import *
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

def record_history(
    kind=None, note=None,
    referenced_project=None, referenced_faculty=None, referenced_request=None,
    referenced_user_primary=None, referenced_user_secondary=None,
    email_qs=None
):
    entry = HistoryEntry()
    entry.occurence_time              = datetime.datetime.now()
    entry.kind                        = kind
    entry.note                        = note
    entry.referenced_project          = referenced_project
    entry.referenced_faculty          = referenced_faculty
    entry.referenced_request          = referenced_request
    entry.referenced_user_primary     = referenced_user_primary
    entry.referenced_user_secondary   = referenced_user_secondary
    entry.save()
    
    if email_qs:
        label = (
                entry.referenced_request        and entry.referenced_request.project.title
            or  entry.referenced_project        and entry.referenced_project.title
            or  entry.referenced_faculty        and entry.referenced_faculty.name
            or  entry.referenced_user_secondary and entry.referenced_user_secondary.first_name+" "+entry.referenced_user_secondary.last_name
            or  "—"
        )
        referenced_enum = (
                entry.referenced_request        and "request"
            or  entry.referenced_project        and "project"
            or  entry.referenced_faculty        and "faculty"
            or  entry.referenced_user_secondary and "user"
            or  "—"
        )
        referenced_id = (
                entry.referenced_request        and entry.referenced_request.id
            or  entry.referenced_project        and entry.referenced_project.id
            or  entry.referenced_faculty        and entry.referenced_faculty.id
            or  entry.referenced_user_secondary and entry.referenced_user_secondary.id
            or  -1
        )
        email_list = []
        for user in email_qs:
            print "EMAIL TO: ", user.first_name, user.last_name
            if user.email:
                email_list.append(user.email)
        
        if len(email_list) > 0:
            context = Context()
            
            context['kind'] = entry.get_kind_nice(),
            context['note'] = entry.note,
            context['referenced_project'] = entry.referenced_project,
            context['referenced_faculty'] = entry.referenced_faculty,
            context['referenced_request'] = entry.referenced_request,
            context['referenced_user_primary'] = entry.referenced_user_primary,
            context['referenced_user_secondary'] = entry.referenced_user_secondary,
            context['label'] = label
            context['referenced_enum'] = referenced_enum
            context['referenced_id'] = referenced_id
            
            msg = EmailMultiAlternatives(
                '[Blackbox] '+entry.kind+': '+label,
                get_template('email.txt').render(context),
                'do-not-reply@teamprivileged.com',
                email_list
            )
            msg.attach_alternative(get_template('email.html').render(context), "text/html")
            #msg.send()

def find_history(historyentry_qs, thing):
    historyevents = []
    
    def c(other_thing):
        return (other_thing != thing) and other_thing
    
    for historyentry in historyentry_qs:
        historyevents.append({
            'occurence_time': historyentry.occurence_time,
            'kind': historyentry.get_kind_nice(),
            'note': historyentry.note,
            'referenced_project': historyentry.referenced_project,
            'referenced_faculty': historyentry.referenced_faculty,
            'referenced_request': historyentry.referenced_request,
            'referenced_user_primary': historyentry.referenced_user_primary,
            'referenced_user_secondary': historyentry.referenced_user_secondary,
            'glyphicon': historyentry.get_kind_glyphicon(),
            'label': (
                    c(historyentry.referenced_request       ) and historyentry.referenced_request.project.title
                or  c(historyentry.referenced_project       ) and historyentry.referenced_project.title
                or  c(historyentry.referenced_faculty       ) and historyentry.referenced_faculty.name
                or  c(historyentry.referenced_user_secondary) and historyentry.referenced_user_secondary.first_name+" "+historyentry.referenced_user_secondary.last_name
                or  "—"
            ),
            'referenced_enum': (
                    c(historyentry.referenced_request)        and "request"
                or  c(historyentry.referenced_project)        and "project"
                or  c(historyentry.referenced_faculty)        and "faculty"
                or  c(historyentry.referenced_user_secondary) and "user"
                or  "—"
            ),
            'referenced_id': (
                    c(historyentry.referenced_request)        and historyentry.referenced_request.id
                or  c(historyentry.referenced_project)        and historyentry.referenced_project.id
                or  c(historyentry.referenced_faculty)        and historyentry.referenced_faculty.id
                or  c(historyentry.referenced_user_secondary) and historyentry.referenced_user_secondary.id
                or  -1
            ),
        })
    return historyevents

