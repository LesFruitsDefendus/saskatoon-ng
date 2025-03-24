from secrets import choice
from member.models import AuthUser


def make_random_password(length=10) -> str:
    allowed_chars = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return ''.join(choice(allowed_chars) for i in range(length))


def reset_password(user: AuthUser) -> str:
    password = make_random_password(12)
    user.set_password(password)
    user.has_temporary_password = True
    user.save()
    return password
