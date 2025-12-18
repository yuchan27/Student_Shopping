from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

# [表單 1] 註冊表單
class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label='設定密碼',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': '請輸入密碼 (至少8碼)'
        })
    )
    
    email = forms.EmailField(
        label='學校信箱',
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'example@nkust.edu.tw'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'nickname', 'email', 'phone', 'password']
        
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '請設定登入帳號'
            }),
            'nickname': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '如何稱呼您? (選填)'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '0912345678 (選填)'
            }),
        }
        
        labels = {
            'username': '登入帳號',
            'nickname': '顯示暱稱',
            'phone': '手機號碼',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not (email.endswith('.edu') or email.endswith('.edu.tw')):
            raise ValidationError("請使用學生信箱 (.edu 或 .edu.tw)")
        
        if User.objects.filter(email=email).exists():
            raise ValidationError("這個信箱已經被註冊過了！")
            
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_student_verified = True
        if commit:
            user.save()
        return user


# [表單 2] 會員資料修改表單 (剛剛報錯就是因為少了這個！)
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        # 只允許修改這三個欄位，帳號 username 不可改
        fields = ['nickname', 'email', 'phone']
        
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '請輸入顯示暱稱'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@nkust.edu.tw'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0912345678'}),
        }
        
        labels = {
            'nickname': '顯示暱稱',
            'email': '聯絡信箱',
            'phone': '手機號碼',
        }