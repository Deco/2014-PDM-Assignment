from django.db import models
from django.contrib.auth.models import User


class Faculty(models.Model):
    name = models.CharField(max_length=1024, null=False)
    members = models.ManyToManyField(User, through='core.FacultyMembership')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "faculties"

class FacultyMembership(models.Model):

    FACULTY_ROLES = ( 
        ('A', 'Approver'), 
    )

    faculty = models.ForeignKey(Faculty, null=False)
    member = models.ForeignKey(User, null=False)
    role = models.CharField(max_length=1, choices=FACULTY_ROLES)

    def __unicode__(self):
        return str(self.member) + ' (' + [b[1] for b in FacultyMembership.FACULTY_ROLES if b[0] == self.role][0] + ')'

class ProjectMembership(models.Model):

    PROJECT_ROLES = ( 
        ('C', 'Collaborator'), 
        ('R', 'Researcher'), 
        ('P', 'Principal'),
        ('M', 'Data Manager'),
    )

    project = models.ForeignKey('core.Project', null=False)
    member = models.ForeignKey(User, null=False)
    role = models.CharField(max_length=1, choices=PROJECT_ROLES)

    def __unicode__(self):
        return str(self.member) + ': ' + self.role
    

class Project(models.Model):
    name = models.CharField(max_length=1024, null=False)
    faculty = models.ForeignKey(Faculty, null=False)
    members = models.ManyToManyField(User, through=ProjectMembership)

    def __unicode__(self):
        return self.name + ' (' + str(self.faculty) + ')'

class SpaceRequest(models.Model):

    STATUS = (
        ('P', 'PENDING'),
        ('A', 'APPROVED'),
        ('R', 'REJECTED'),
    )

    project = models.ForeignKey(Project, null=False)
    size = models.PositiveIntegerField(null=False)
    requested_by = models.ForeignKey(User, related_name='requests', null=False)
    comment = models.TextField(null=True, blank=True)
    date_requested = models.DateTimeField(null=False)
    status = models.CharField(max_length=1, choices=STATUS, default='P')
    action_date = models.DateTimeField(null=True, blank=True)
    actioned_by = models.ForeignKey(User, related_name='actions', null=True, blank=True)

    def __unicode__(self):
        return str(self.project) + ' ' + str(self.date_requested) + ' (' + str(self.size) + ')'







