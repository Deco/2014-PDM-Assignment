from django.forms import ModelForm
from django.forms import fields
from core.models import *

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'faculty']
        
class ProjectMembershipForm(ModelForm):
    class Meta:
        model = ProjectMembership
        fields = ['member', 'role']

class FacultyMembershipForm(ModelForm):
    class Meta:
        model = FacultyMembership
        fields = ['member', 'role']

class RequestForm(ModelForm):
    
    def __init__(self, user=None, *args, **kwargs):
        super(RequestForm, self).__init__(*args, **kwargs)
        membershipObjs = ProjectMembership.objects.filter(member_id=user)
        self.fields['project'].queryset = self.fields['project'].queryset.filter(projectmembership__in=membershipObjs)
        
    class Meta:
        model = SpaceRequest
        fields = ['project', 'size_mb']