import math
from typing import SupportsFloat, SupportsIndex, Union

from django.core.exceptions import ValidationError
from typeguard import typechecked


@typechecked
def validate_is_not_nan(n: Union[SupportsFloat, SupportsIndex]) -> None:
    if math.isnan(n):
        raise ValidationError("This field does not accept nan")
