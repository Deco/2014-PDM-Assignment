from core.models import *
import datetime

def record_history(
    kind=None, note=None,
    referenced_project=None, referenced_faculty=None, referenced_request=None,
    referenced_user_primary=None, referenced_user_secondary=None
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



