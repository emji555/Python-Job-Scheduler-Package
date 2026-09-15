"""Optional Django integration.

Install: pip install "workloom[django]"

Add to INSTALLED_APPS:
    "workloom.integrations.django"
"""

from __future__ import annotations

default_app_config = "workloom.integrations.django.apps.WorkloomConfig"

__all__ = ["default_app_config"]
