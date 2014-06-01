from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.comments.forms import CommentDetailsForm

#print '\n'.join("%s: %s" % item for item in vars(CommentDetailsForm).items())

CommentDetailsForm.base_fields['email'].required = False

