from hypothesis import given, strategies as st
from django.core.exceptions import ValidationError
import pytest

from sitebase.validators import validate_is_not_nan


@given(num=st.floats(allow_nan=False))
def test_validate_is_not_nan_does_not_raise_exceptions_when_no_nan(num):
    validate_is_not_nan(num)
    assert True


def test_validate_is_not_nan_does_not_accept_nan():
    with pytest.raises(ValidationError):
        validate_is_not_nan(float("nan"))
