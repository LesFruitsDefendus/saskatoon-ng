from saskatoon.autocomplete import Autocomplete


def test_Autocomplete_init():
    """Test that the Autocomplete class can be initialized"""

    autocomplete = Autocomplete()

    assert isinstance(autocomplete, Autocomplete)
