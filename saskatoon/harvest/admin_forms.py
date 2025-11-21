from django.contrib import admin
from dal import autocomplete
from django import forms
from harvest.forms import RFPForm, HarvestYieldForm

from harvest.models import (
    Equipment,
    HarvestYield,
    HarvestImage,
    RequestForParticipation as RFP,
)


class RFPPersonInline(admin.TabularInline[RFP, RFP]):
    model = RFP
    form = RFPForm
    verbose_name = "Cueilleurs pour cette récolte"
    verbose_name_plural = "Cueilleurs pour cette récolte"
    exclude = ['date_created', 'confirmation_date']
    extra = 3


class HarvestYieldInline(admin.TabularInline[HarvestYield, HarvestYield]):
    model = HarvestYield
    form = HarvestYieldForm


class HarvestImageInline(admin.TabularInline[HarvestImage, HarvestImage]):
    model = HarvestImage
    extra = 3


class EquipmentAdminForm(forms.ModelForm[Equipment]):
    def clean(self):
        cleaned_data = super(EquipmentAdminForm, self).clean()
        bool1 = bool(self.cleaned_data['property'])
        bool2 = bool(self.cleaned_data['owner'])
        if not (bool1 != bool2):
            raise forms.ValidationError('Fill in one of the two fields: property or owner.')
        return cleaned_data

    class Meta:
        model = Equipment
        fields = '__all__'
        widgets = {
            'property': autocomplete.ModelSelect2('property-autocomplete'),
            'owner': autocomplete.ModelSelect2('actor-autocomplete'),
        }
