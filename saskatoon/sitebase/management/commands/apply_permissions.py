from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from member.models import Role
from saskatoon.permissions import ALL_PERMISSIONS

PermKey = tuple[str, str]  # (app_label, codename)

class Command(BaseCommand):
    help = "Apply Auth.Group permissions as defined in each app's permissions.py file"

    def handle(self, *args, **options):
        role_perms: dict[Role, set[PermKey]] = {role: set() for role in Role}

        # Collect permission keys (app_label, codename) for each role
        for app_label, models in ALL_PERMISSIONS.items():
            for model_name, actions in models.items():
                for action, roles in actions.items():
                    codename = f"{action}_{model_name}"
                    for role in roles:
                        role_perms[role].add((app_label, codename))

        # Resolve and apply permissions for each group
        for role, perm_keys in role_perms.items():
            if not perm_keys:
                continue

            group, _ = Group.objects.get_or_create(name=role)

            query = Q()
            for app_label, codename in perm_keys:
                query |= Q(content_type__app_label=app_label, codename=codename)
            permissions = list(Permission.objects.filter(query).select_related("content_type"))

            found = {(p.content_type.app_label, p.codename) for p in permissions}
            for key in perm_keys - found:
                self.stderr.write(self.style.WARNING(
                    f"Permission '{key[0]}.{key[1]}' not found in database, skipping"
                ))

            group.permissions.set(permissions)

        self.stdout.write(self.style.SUCCESS("\nPermissions applied."))
