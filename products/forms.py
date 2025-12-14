from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # 包含剛剛新增的 description
        fields = ['image', 'name', 'price', 'stock', 'description']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '請輸入商品名稱'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '商品描述...'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': '商品名稱',
            'price': '價格',
            'stock': '庫存數量',
            'description': '商品描述',
            'image': '商品圖片',
        }