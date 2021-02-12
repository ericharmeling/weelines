from django import forms

class TickerForm(forms.Form):
    symbol = forms.CharField(label='ticker symbol', max_length=5)
    start = forms.DateTimeField(label='start date')