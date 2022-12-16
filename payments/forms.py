from django import forms


class DetailForm (forms.Form):
    quantity = forms.IntegerField(
        label='Количество',
        widget=forms.NumberInput,
        min_value=1,
    )


class CatalogForm(forms.Form):
    quantity = forms.IntegerField(
            label='Количество',
            widget=forms.NumberInput,
            min_value=1,
        )