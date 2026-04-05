from django import forms

class RenewBookForm(forms.Form):
    # Añadimos el widget con el tipo 'date' para que sea amigable
    renewal_date = forms.DateField(
        help_text="Enter a date between now and 4 weeks (default 3).",
        widget=forms.DateInput(attrs={'type': 'date'}) 
    )