from member.models import AuthUser


def is_translator(user: AuthUser) -> bool:
    return user.groups.filter(name__in=("admin", "core")) and user.is_staff
