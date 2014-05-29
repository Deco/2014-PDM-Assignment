from django.forms import ModelForm, fields, Textarea, ModelChoiceField, Select
from core.models import *

class UserChoiceField(ModelChoiceField):
     def label_from_instance(self, obj):
         return "%s %s" % (obj.first_name, obj.last_name)

class FacultyForm(ModelForm):
    class Meta:
        model = Faculty
        fields = ['name']
        widgets = {
            'name': Textarea(),
        }

class FacultyMembershipForm(ModelForm):
    class Meta:
        model = FacultyMembership
        fields = ['member', 'role']

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'faculty']
        widgets = {
            'title': Textarea(),
        }
        
class ProjectMembershipForm(ModelForm):
    member = UserChoiceField(
        queryset=User.objects.all(),
        widget=Select(attrs={'class': 'member-select'})
    )
    class Meta:
        model = ProjectMembership
        fields = ['member', 'role']

class SpaceRequestForm(ModelForm):
    #def __init__(self, user=None, *args, **kwargs):
    #    super(SpaceRequestForm, self).__init__(*args, **kwargs)
        #membershipObjs = ProjectMembership.objects.filter(member=user)
        #self.fields['project'].queryset = self.fields['project'].queryset.filter(projectmembership__in=membershipObjs)
        
    class Meta:
        model = SpaceRequest
        #fields = ['project', 'size_mb']
        fields = ['size_mb']
