from django.apps import apps
from django.core.management.base import BaseCommand

from saskatoon.permissions import ALL_PERMISSIONS


class Command(BaseCommand):
    help = "Check that every model in each app has an entry in PERMISSIONS"

    def handle(self, *args, **options):
        missing = []
        extra = []
        ok = True

        for app_label, permissions in ALL_PERMISSIONS.items():
            app_config = apps.get_app_config(app_label)
            app_models = {
                m._meta.model_name for m in app_config.get_models()
            }

            declared = set(permissions.keys())

            for name in sorted(app_models - declared):
                missing.append((app_label, name))

            for name in sorted(declared - app_models):
                extra.append((app_label, name))


        if extra:
            ok = False
            self.stderr.write(self.style.ERROR(
                "The following entries in ALL_PERMISSIONS do not correspond to any model:"
            ))
            for app_label, name in extra:
                self.stderr.write(f"  - {app_label}.{name}")

        if missing:
            ok = False
            self.stderr.write(self.style.ERROR(
                "The following models are missing from ALL_PERMISSIONS:"
            ))
            for app_label, name in missing:
                self.stderr.write(f"  {app_label}.{name}")


        if not ok:
            self.stderr.write(
                "Please update the corresponding permissions.py file(s)."
            )
            raise SystemExit(1)
