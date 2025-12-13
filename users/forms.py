from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # 這裡檢查是否為 .edu 結尾
        if not (email.endswith('.edu') or email.endswith('.edu.tw')):
            raise ValidationError("請使用學生信箱 (.edu)")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_student_verified = True
        if commit:
            user.save()
        return user