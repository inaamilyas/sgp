from django import forms
from StudyGuidelinePortal.models import *


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['dep_name']

        widgets = {
            'dep_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_name', 'course_pic', 'department']

        widgets = {
            'course_name': forms.TextInput(attrs={'class': 'form-control'}),
            # 'course_pic': forms.ImageField(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
        }


class LesssonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['lesson_title', 'lesson_desc', 'course', 'lesson_tags', 'lesson_summary']

        widgets = {
            'lesson_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Enter title of the lesson'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'lesson_summary': forms.Textarea(attrs={'class': 'form-control', 'placeholder':'Write a short summary of the lesson here (max 200 words)'}),
            'lesson_tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Enter relevant keywords for search engine optimization'}),
        }


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
            'query': forms.Select(attrs={'class': 'form-control'}),
        }
