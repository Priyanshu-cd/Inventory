from django import forms
from dash import models
from django.utils import timezone


class ProjectForm(forms.ModelForm):
    class Meta:
        model=models.Project
        fields="__all__"
        exclude=["organization","buy_total","sell_total","profit_total","lifetime_advance","advance_total"]
        labels={"name":"Enter Name","description":"Description","is_active":"Active Project"}

class AdvanceForm(forms.ModelForm):
    project = forms.ModelChoiceField(queryset=models.Project.objects.filter(is_active=True), required=True)

    class Meta:
        model=models.AdvanceDetail
        fields="__all__"
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

class ExpenseForm(forms.ModelForm):
    project = forms.ModelChoiceField(queryset=models.Project.objects.filter(is_active=True), required=True)

    class Meta:
        model=models.Inventory
        fields="__all__"
        exclude=['total_buy','total_sell','total_profit']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

class FilterForm(forms.Form):
    project = forms.ModelChoiceField(queryset=models.Project.objects.all(), required=False)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'value':f'{timezone.now}'}),
        initial=timezone.now,required=False)
