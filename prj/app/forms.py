from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Comment, Rating


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        labels = {"text": "Komentář"}
        widgets = {
            "text": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Napiš svůj názor na film…",
                "class": "form-control",
            }),
        }


class RatingForm(forms.ModelForm):
    value = forms.IntegerField(
        label="Hodnocení (1–10)",
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={"min": 1, "max": 10, "class": "form-control"}),
    )

    class Meta:
        model = Rating
        fields = ["value"]


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplikujeme Bootstrap třídu form-control na všechna pole formuláře.
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
