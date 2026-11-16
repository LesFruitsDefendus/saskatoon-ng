from types import SimpleNamespace

from harvest.mixins import UploaderOrAdminRequiredMixin


class FakeView(UploaderOrAdminRequiredMixin):
    def __init__(self, user, image):
        self.request = SimpleNamespace(user=user)  # type: ignore[assignment]
        self._image = image

    def get_object(self):
        return self._image


def check(user, uploader, monkeypatch, is_admin=False):
    monkeypatch.setattr('harvest.mixins.is_core_or_admin', lambda u: is_admin)
    image = SimpleNamespace(uploaded_by=uploader)
    return FakeView(user, image).has_permission()


def test_uploader_is_allowed(monkeypatch):
    user = object()
    assert check(user, uploader=user, monkeypatch=monkeypatch) is True


def test_other_user_is_denied(monkeypatch):
    assert check(object(), uploader=object(), monkeypatch=monkeypatch) is False


def test_core_or_admin_is_allowed_on_others_photos(monkeypatch):
    assert check(object(), uploader=object(), monkeypatch=monkeypatch, is_admin=True) is True
