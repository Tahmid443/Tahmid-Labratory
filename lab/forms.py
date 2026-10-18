from django import forms
from .models import Section, SubTopic, Topic


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ["name", "description", "icon", "order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "icon": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "🐍"}
            ),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }


class SubTopicForm(forms.ModelForm):
    class Meta:
        model = SubTopic
        fields = ["name", "description", "order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ["title", "description", "language", "code", "output", "order"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "language": forms.TextInput(attrs={"class": "form-control"}),
            "code": forms.Textarea(
                attrs={"class": "form-control code-input", "rows": 8}
            ),
            "output": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }
