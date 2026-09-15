"""Optional Django integration.

Install: pip install "package-name[django]"

Add to INSTALLED_APPS:
    "package_name.integrations.django"
"""

from __future__ import annotations

default_app_config = "package_name.integrations.django.apps.PackageNameConfig"

__all__ = ["default_app_config"]
