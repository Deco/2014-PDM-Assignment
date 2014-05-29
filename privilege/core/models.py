from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


def user_unicode(self):
    return  u'%s %s' % (self.first_name, self.last_name)

User.__unicode__ = user_unicode

class Faculty(models.Model):
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
    size_mb          = models.PositiveIntegerField(null=False)
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
    KIND = (
        ('S', 'SPACE_REQUEST_CREATED'),
        ('A', 'SPACE_REQUEST_APPROVED'),
        ('C', 'SPACE_REQUEST_COMMENT'),
        ('P', 'PROJECT_CREATED'),
        ('M', 'MEMBER_CREATED'),
        ('J', 'MEMBER_JOINED'),
    )
    # These will serve as notifications, too
    # To relevency of a HistoryEntry to a user is determined by their membership to the referenced object
    
    occurence_time              = models.DateTimeField(auto_now_add=True)
    referenced_project          = models.ForeignKey(Project, null=True)
    referenced_faculty          = models.ForeignKey(Faculty, null=True)
    referenced_request          = models.ForeignKey(SpaceRequest, null=True)
    referenced_member_primary   = models.ForeignKey(User, null=True, related_name='historyentry_referedto_primary_set')
    referenced_member_secondary = models.ForeignKey(User, null=True, related_name='historyentry_referedto_secondary_set')
