import re  # [新增] 記得要在檔案最上面引入正規表達式模組
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class RegisterForm(forms.ModelForm):
    # 1. 密碼欄位
    password = forms.CharField(
        label='設定密碼',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': '請輸入密碼 (至少8碼，含英數)'
        }),
        help_text='密碼長度需至少 8 碼，且必須包含英文與數字。' # [新增] 提示文字
    )

    # 2. [新增] 確認密碼欄位
    confirm_password = forms.CharField(
        label='確認密碼',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': '請再次輸入密碼'
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
        fields = ['username', 'nickname', 'email', 'phone', 'password'] # confirm_password 不用寫在這裡，因為它不是 Model 的欄位
        
        # [重點] 設定欄位在網頁上的顯示順序
        # 確保 confirm_password 排在 password 後面
        field_order = ['username', 'nickname', 'email', 'phone', 'password', 'confirm_password']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '請設定登入帳號'}),
            'nickname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '如何稱呼您? (選填)'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0912345678 (選填)'}),
        }
        
        labels = {
            'username': '登入帳號',
            'nickname': '顯示暱稱',
            'phone': '手機號碼',
        }

    # [驗證 1] 檢查密碼複雜度 (長度 >= 8, 需有英文+數字)
    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        # 檢查長度
        if len(password) < 8:
            raise ValidationError("密碼長度不足，至少需要 8 個字元。")
        
        # 檢查是否包含數字
        if not re.search(r'\d', password):
            raise ValidationError("密碼必須包含至少一個數字。")
            
        # 檢查是否包含英文 (不分大小寫)
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError("密碼必須包含至少一個英文字母。")
            
        return password

    # [驗證 2] 檢查信箱格式 & 是否重複
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not (email.endswith('.edu') or email.endswith('.edu.tw')):
            raise ValidationError("請使用學生信箱 (.edu 或 .edu.tw)")
        
        if User.objects.filter(email=email).exists():
            raise ValidationError("這個信箱已經被註冊過了！")
        return email

    # [驗證 3] 檢查兩次密碼是否一致
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # 只有當兩個密碼都存在時才比較
        if password and confirm_password:
            if password != confirm_password:
                # 針對 confirm_password 欄位報錯，紅字會顯示在確認密碼下方
                self.add_error('confirm_password', "兩次輸入的密碼不一致！")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_student_verified = True
        if commit:
            user.save()
        return user


# [表單 2] 會員資料修改表單
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