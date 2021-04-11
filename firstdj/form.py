from django import forms


stock= [
    ('AAPL', 'AAPL'),
    ('MSFT', 'MSFT'),
    ('TSLA', 'TSLA'),
    ]

class stocklist(forms.Form):
    stock_tick= forms.CharField(label='Select Stock', widget=forms.Select(choices=stock))
