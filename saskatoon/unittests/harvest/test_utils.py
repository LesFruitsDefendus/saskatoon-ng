from datetime import datetime, timedelta
from io import BytesIO

from django.utils import timezone
from PIL import Image

from harvest.utils import buffer_reservation_time, resize_and_save_image


def test_buffer_reservation_time() -> None:
    date = datetime(2222, 5, 22, 18, 0, 0, 0, timezone.get_current_timezone())

    # Mainly I wanted to test that adding a negative timedelta would work
    delta = timedelta(hours=-1)

    assert "05:00 PM" == buffer_reservation_time(date, delta)


# image resizer tests
def make_image_file(size=(100, 100), mode='RGB', fmt='PNG', color='red', **save_kwargs):
    buffer = BytesIO()
    Image.new(mode, size, color).save(buffer, format=fmt, **save_kwargs)
    buffer.seek(0)
    return buffer


def open_result(result):
    assert result is not None, "resize_and_save_image returned None"
    result.file.seek(0)
    return Image.open(result.file)


def test_large_landscape_is_resized_to_max_side():
    result = resize_and_save_image(make_image_file((4000, 2000)), 'photo.png')

    img = open_result(result)
    assert img.size == (1080, 540)
    assert img.format == 'JPEG'


def test_large_portrait_is_resized_to_max_side():
    result = resize_and_save_image(make_image_file((2000, 4000)), 'photo.png')

    assert open_result(result).size == (540, 1080)


def test_small_image_is_not_upscaled():
    result = resize_and_save_image(make_image_file((300, 200)), 'photo.png')

    assert open_result(result).size == (300, 200)


def test_output_is_named_and_typed_as_jpeg():
    result = resize_and_save_image(make_image_file(), 'my.photo.png')

    assert result is not None
    assert result.name == 'my.photo.jpg'
    assert result.content_type == 'image/jpeg'
    assert result.size == len(result.read())


def test_transparent_png_is_flattened_onto_white():
    source = make_image_file((50, 50), mode='RGBA', color=(0, 0, 0, 0))

    result = resize_and_save_image(source, 'logo.png')

    pixel = open_result(result).convert('RGB').getpixel((25, 25))
    assert all(channel > 240 for channel in pixel)


def test_exif_orientation_is_applied():
    exif = Image.Exif()
    exif[0x0112] = 6  # camera rotated: pixels need a 90-degree turn
    source = make_image_file((200, 100), fmt='JPEG', exif=exif)

    result = resize_and_save_image(source, 'phone.jpg')

    assert open_result(result).size == (100, 200)


def test_non_image_returns_none():
    assert resize_and_save_image(BytesIO(b'not an image'), 'fake.jpg') is None
