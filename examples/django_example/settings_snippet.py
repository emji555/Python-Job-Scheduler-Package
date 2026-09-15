"""Minimal Django settings snippet for the optional integration.

This is documentation-as-code — not a full Django project.
"""

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "workloom.integrations.django",
]

WORKLOOM_BACKEND = "eager"
WORKLOOM_DEFAULT_QUEUE = "default"
WORKLOOM_TIMEZONE = "UTC"

# Example usage in a view / service:
#
# from workloom import job
# from workloom.integrations.django.helpers import dispatch_after_commit
#
# @job(queue="dhis2", retries=5)
# def sync_patient(patient_id: int) -> None:
#     ...
#
# dispatch_after_commit(sync_patient, patient.id)
