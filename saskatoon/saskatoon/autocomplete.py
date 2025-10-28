from dal import autocomplete
from typeguard import typechecked


@typechecked
class Autocomplete(autocomplete.Select2QuerySetView):
    """Helper class to make testing easier.
    Request is not always present in unit tests so we need to check for it"""

    def is_authenticated(self) -> bool:
        has_request = hasattr(autocomplete, 'request')

        return has_request and self.request.user.is_authenticated
