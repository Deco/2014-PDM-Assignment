from django.contrib import admin
from models import Faculty, Project, SpaceRequest, ProjectMembership, FacultyMembership

admin.site.register(Faculty)
admin.site.register(Project)
admin.site.register(SpaceRequest)
admin.site.register(FacultyMembership)
admin.site.register(ProjectMembership)
