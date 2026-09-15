"""Minimal Django settings snippet for the optional integration.

This is documentation-as-code — not a full Django project.
"""

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "package_name.integrations.django",
]

PACKAGE_BACKEND = "eager"
PACKAGE_DEFAULT_QUEUE = "default"
PACKAGE_TIMEZONE = "UTC"

# Example usage in a view / service:
#
# from package_name import job
# from package_name.integrations.django.helpers import dispatch_after_commit
#
# @job(queue="dhis2", retries=5)
# def sync_patient(patient_id: int) -> None:
#     ...
#
# dispatch_after_commit(sync_patient, patient.id)
