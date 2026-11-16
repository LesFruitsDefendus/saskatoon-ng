from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from harvest.forms import (
    CommentForm,
    EquipmentForm,
    HarvestForm,
    HarvestYieldForm,
    PropertyCreateForm,
    PropertyForm,
    PropertyImageForm,
    PublicPropertyForm,
    RFPForm,
)

""" I had to remove RFPManageForm from the list of classes
    since it needs more setup for a successful initialization and
    it's not currently my focus
"""
form_classes = [
    RFPForm,
    CommentForm,
    PropertyForm,
    PropertyCreateForm,
    PublicPropertyForm,
    HarvestForm,
    HarvestYieldForm,
    EquipmentForm,
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


# image forms
def upload(name, content, content_type='image/png'):
    return SimpleUploadedFile(name, content, content_type=content_type)


def png_bytes(size=(100, 100), fmt='PNG'):
    buffer = BytesIO()
    Image.new('RGB', size, 'red').save(buffer, format=fmt)
    return buffer.getvalue()


def test_valid_png_is_converted_and_resized():
    form = PropertyImageForm({}, {'image': upload('big.png', png_bytes((3000, 2000)))})

    assert form.is_valid(), form.errors
    image = form.cleaned_data['image']
    assert image.name.endswith('.jpg')
    assert max(Image.open(image).size) == 1080


def test_disallowed_extension_is_rejected():
    form = PropertyImageForm({}, {'image': upload('anim.gif', png_bytes(fmt='GIF'), 'image/gif')})

    assert not form.is_valid()
    assert 'image' in form.errors


def test_non_image_with_image_extension_is_rejected():
    form = PropertyImageForm({}, {'image': upload('fake.jpg', b'just text', 'image/jpeg')})

    assert not form.is_valid()
    assert 'image' in form.errors


def test_oversize_upload_is_rejected():
    file = upload('huge.png', png_bytes())
    file.size = 26 * 1024 * 1024  # pretend the upload is 26MB

    form = PropertyImageForm({}, {'image': file})

    assert not form.is_valid()
    assert 'too large' in str(form.errors['image'])


""" TODO: add tests for harvest form clean, clean_end_date,
       clean_trees, clean_about and save (and other forms).

       I ran into issues with the harvest fixture and quill fields,
       so I decided to push back testing till I have a better handle of them
"""
