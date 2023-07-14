from django import forms 
from .models import Query, Answer

class QueryForm(forms.ModelForm):
    class Meta:
        model = Query
        fields = ['query_title', 'query_desc', 'course']

        widgets = {
            'query_title': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['ans_desc']

        widgets = {
            # 'query': forms.Select(attrs={'class': 'form-control'}),
        }