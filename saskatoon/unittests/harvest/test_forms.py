from harvest.forms import HarvestForm


def test_HarvestForm_init():
    form = HarvestForm()

    assert isinstance(form, HarvestForm)


def test_HarvestForm_empty_is_invalid():
    form = HarvestForm()

    assert not form.is_valid()
