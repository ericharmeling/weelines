from django import forms

class TickerForm(forms.Form):
    symbol = forms.CharField(label='ticker symbol', max_length=5)
    delta = forms.IntegerField(label='time delta')

class PositionForm(forms.Form):
    account = forms.UUIDField(label='account ID')
    symbol = forms.CharField(label='ticker symbol', max_length=5)
    quantity = forms.IntegerField(label='quantity')


class LoginForm(forms.Form):
    user = forms.CharField(label='user', max_length=15)
    password = forms.CharField(label='password', max_length=35)
