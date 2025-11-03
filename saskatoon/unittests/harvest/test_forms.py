import pytest

from harvest.forms import (
    RFPForm, CommentForm,
    PropertyForm, PropertyCreateForm, PublicPropertyForm,
    HarvestForm, HarvestYieldForm, EquipmentForm
)

""" I had to remove RFPManageForm from the list of classes
    since it needs more setup for a successful initialization and
    it's not currently my focus
"""
form_classes = [
    RFPForm, CommentForm,
    PropertyForm, PropertyCreateForm, PublicPropertyForm,
    HarvestForm, HarvestYieldForm, EquipmentForm
]


@pytest.mark.parametrize("Form", form_classes)
def test_Form_init(Form):
    """Test that all Form classes can be initialized"""

    form = Form()

    assert isinstance(form, Form)


@pytest.mark.parametrize("Form", form_classes)
def test_Form_empty_is_invalid(Form):
    """Test that empty forms are invalid"""

    form = Form()

    assert not form.is_valid()


""" TODO: add tests for harvest form clean, clean_end_date,
       clean_trees, clean_about and save (and other forms).

       I ran into issues with the harvest fixture and quill fields,
       so I decided to push back testing till I have a better handle of them
"""
