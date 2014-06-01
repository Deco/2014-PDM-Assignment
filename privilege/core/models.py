from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


User.url_type = "user"
def user_unicode(self):
    return  u'%s %s' % (self.first_name, self.last_name)
User.__unicode__ = user_unicode

class Faculty(models.Model):
    url_type = "faculty"
    name    = models.CharField(max_length=1024, null=False)
    members = models.ManyToManyField(User, through='core.FacultyMembership')
    update_time = models.DateTimeField(auto_now_add=True, blank=True)
    creation_time = models.DateTimeField(auto_now_add=True, blank=True)
    
    def add_membership(self, user, role):
        FacultyMembership.objects.create(
            faculty=self,
            member=user,
            role=role
        )
    
    def get_membership(self, user):
        membership = None
        try:
            membership = FacultyMembership.objects.get(
                faculty=self,
                member=user
            )
        except FacultyMembership.DoesNotExist:
            membership = None
        
        return membership
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "faculties"

class FacultyMembership(models.Model):
    APPROVER = 'A'
    MANAGER = 'M'
    
    FACULTY_ROLES = ( 
        (APPROVER, 'Approver'),
        (MANAGER, 'Manager'),
    )
    
    faculty = models.ForeignKey(Faculty, null=False)
    member  = models.ForeignKey(User, null=False)
    role    = models.CharField(max_length=1, choices=FACULTY_ROLES)
    
    def __unicode__(self):
        return str(self.member) + ' (' + [b[1] for b in FacultyMembership.FACULTY_ROLES if b[0] == self.role][0] + ')'
    
    def get_role_nice(self):
        return dict(self.FACULTY_ROLES).get(self.role, 'Unknown')


class Project(models.Model):
    url_type = "project"
    title  = models.CharField(max_length=1024, null=False)
    faculty = models.ForeignKey(Faculty, null=False)
    storage_capacity_mb = models.PositiveIntegerField(default=0)
    storage_used_mb = models.PositiveIntegerField(default=0)
    creation_time = models.DateTimeField(auto_now_add=True, blank=True)
    update_time = models.DateTimeField(auto_now_add=True, blank=True)
    
    members = models.ManyToManyField(User, through='core.ProjectMembership')
    
    def add_membership(self, user, role):
        ProjectMembership.objects.create(
            project=self,
            member=user,
            role=role
        )
    
    def get_membership(self, user):
        membership = None
        try:
            membership = ProjectMembership.objects.get(
                project=self,
                member=user
            )
        except ProjectMembership.DoesNotExist:
            membership = None
        
        return membership
    
    def __unicode__(self):
        return self.title + ' (' + str(self.faculty) + ')'

class ProjectMembership(models.Model):
    class Meta:
        ordering = ['-id']
        
    COLLABORATOR = 'C'
    RESEARCHER = 'R'
    PRINCIPALINVESTIGATOR = 'P'
    DATAMANAGER = 'M'
    
    PROJECT_ROLES = ( 
        (COLLABORATOR, 'Collaborator'), 
        (RESEARCHER, 'Researcher'), 
        (PRINCIPALINVESTIGATOR, 'Principal Investigator'),
        (DATAMANAGER, 'Data Manager'),
    )
    
    project = models.ForeignKey('core.Project', null=False)
    member  = models.ForeignKey(User, null=False)
    role    = models.CharField(max_length=1, choices=PROJECT_ROLES, null=False)
    
    def __unicode__(self):
        return str(self.member) + ': ' + self.role
    
    def get_role_nice(self):
        return dict(self.PROJECT_ROLES).get(self.role, 'Unknown')

class SpaceRequest(models.Model):
    url_type = "request"
    STATUS_INACTIVE = 'I'
    STATUS_PENDING = 'P'
    STATUS_APPROVED = 'A'
    STATUS_REJECTED = 'R'
    
    STATUS = (
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    )
    
    project         = models.ForeignKey(Project, null=False)
    size_mb         = models.PositiveIntegerField(null=False)
    comment         = models.TextField(null=True, blank=True)
    status          = models.CharField(max_length=1, choices=STATUS, default=STATUS_PENDING)
    request_time    = models.DateTimeField(auto_now_add=True, blank=True)
    requested_by    = models.ForeignKey(User, related_name='requests', null=False)
    action_time     = models.DateTimeField(null=True, blank=True)
    actioned_by     = models.ForeignKey(User, related_name='actions', null=True, blank=True)
    update_time     = models.DateTimeField(auto_now_add=True, blank=True)
    
    def __unicode__(self):
        return str(self.project) + ' ' + str(self.request_time) + ' (' + str(self.size_mb) + ')'
    
    def get_status_nice(self):
        return dict(self.STATUS).get(self.status, 'Unknown')

class HistoryEntry(models.Model):
    FACULTY_CREATED             = 101
    FACULTY_EDITED              = 102
    FACULTY_DELETED             = 103
    FACULTY_MEMBER_ADDED        = 104
    FACULTY_MEMBER_CHANGED      = 105
    FACULTY_MEMBER_REMOVED      = 106
    FACULTY_COMMENT_ADDED       = 107
    PROJECT_CREATED             = 201
    PROJECT_EDITED              = 202
    PROJECT_DELETED             = 203
    PROJECT_MEMBER_ADDED        = 204
    PROJECT_MEMBER_CHANGED      = 205
    PROJECT_MEMBER_REMOVED      = 206
    PROJECT_COMMENT_ADDED       = 207
    SPACE_REQUEST_CREATED       = 301
    SPACE_REQUEST_EDITED        = 302
    SPACE_REQUEST_DELETED       = 303
    SPACE_REQUEST_ACTIVATED     = 304
    SPACE_REQUEST_APPROVED      = 305
    SPACE_REQUEST_REJECTED      = 306
    SPACE_REQUEST_COMMENT_ADDED = 307
    USER_CREATED                = 401
    
    KIND = (
        (FACULTY_CREATED            , 'Faculty created'),
        (FACULTY_EDITED             , 'Faculty edited'),
        (FACULTY_DELETED            , 'Faculty deleted'),
        (FACULTY_MEMBER_ADDED       , 'Faculty member added'),
        (FACULTY_MEMBER_CHANGED     , 'Faculty member changed'),
        (FACULTY_MEMBER_REMOVED     , 'Faculty member removed'),
        (FACULTY_COMMENT_ADDED      , 'Faculty comment added'),
        (PROJECT_CREATED            , 'Project created'),
        (PROJECT_EDITED             , 'Project edited'),
        (PROJECT_DELETED            , 'Project deleted'),
        (PROJECT_MEMBER_ADDED       , 'Project member added'),
        (PROJECT_MEMBER_CHANGED     , 'Project member changed'),
        (PROJECT_MEMBER_REMOVED     , 'Project member removed'),
        (PROJECT_COMMENT_ADDED      , 'Project comment added'),
        (SPACE_REQUEST_CREATED      , 'Space request created'),
        (SPACE_REQUEST_EDITED       , 'Space request edited'),
        (SPACE_REQUEST_DELETED      , 'Space request deleted'),
        (SPACE_REQUEST_ACTIVATED    , 'Space request activated'),
        (SPACE_REQUEST_APPROVED     , 'Space request approved'),
        (SPACE_REQUEST_REJECTED     , 'Space request rejected'),
        (SPACE_REQUEST_COMMENT_ADDED, 'Space request comment added'),
        (USER_CREATED               , 'User created'),
    )
    
    KIND_GLYPHICON = {} # lol, why not
    KIND_GLYPHICON[FACULTY_CREATED            ] = "bookmark"
    KIND_GLYPHICON[FACULTY_EDITED             ] = "asterisk"
    KIND_GLYPHICON[FACULTY_DELETED            ] = "thumbs-down"
    KIND_GLYPHICON[FACULTY_MEMBER_ADDED       ] = "bullhorn"
    KIND_GLYPHICON[FACULTY_MEMBER_CHANGED     ] = "bullhorn"
    KIND_GLYPHICON[FACULTY_MEMBER_REMOVED     ] = "thumbs-down"
    KIND_GLYPHICON[FACULTY_COMMENT_ADDED      ] = "euro"
    KIND_GLYPHICON[PROJECT_CREATED            ] = "floppy-open"
    KIND_GLYPHICON[PROJECT_EDITED             ] = "floppy-saved"
    KIND_GLYPHICON[PROJECT_DELETED            ] = "floppy-removed"
    KIND_GLYPHICON[PROJECT_MEMBER_ADDED       ] = "user"
    KIND_GLYPHICON[PROJECT_MEMBER_CHANGED     ] = "user"
    KIND_GLYPHICON[PROJECT_MEMBER_REMOVED     ] = "thumbs-down"
    KIND_GLYPHICON[PROJECT_COMMENT_ADDED      ] = "euro"
    KIND_GLYPHICON[SPACE_REQUEST_CREATED      ] = "plus-sign"
    KIND_GLYPHICON[SPACE_REQUEST_EDITED       ] = "info-sign"
    KIND_GLYPHICON[SPACE_REQUEST_DELETED      ] = "remove-sign"
    KIND_GLYPHICON[SPACE_REQUEST_ACTIVATED    ] = "circle-arrow-right"
    KIND_GLYPHICON[SPACE_REQUEST_APPROVED     ] = "ok-sign"
    KIND_GLYPHICON[SPACE_REQUEST_REJECTED     ] = "remove-sign"
    KIND_GLYPHICON[SPACE_REQUEST_COMMENT_ADDED] = "question-sign"
    KIND_GLYPHICON[USER_CREATED               ] = "euro"
    
    # These will serve as notifications, too
    # To relevency of a HistoryEntry to a user is determined by their membership to the referenced object
    
    occurence_time              = models.DateTimeField(auto_now_add=True)
    kind                        = models.IntegerField(choices=KIND)
    note                        = models.TextField(null=True, blank=True)
    referenced_project          = models.ForeignKey(Project, null=True)
    referenced_faculty          = models.ForeignKey(Faculty, null=True)
    referenced_request          = models.ForeignKey(SpaceRequest, null=True)
    referenced_user_primary     = models.ForeignKey(User, null=True, related_name='historyentry_referedto_primary_set')
    referenced_user_secondary   = models.ForeignKey(User, null=True, related_name='historyentry_referedto_secondary_set')
    
    def get_kind_nice(self):
        return dict(self.KIND).get(self.kind, 'Unknown')
        
    def get_kind_glyphicon(self):
        return self.KIND_GLYPHICON.get(self.kind, 'euro')
