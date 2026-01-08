from django import forms
from .models import Product, Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '例如：3C周邊、教科書、生活用品...'
            }),
        }
        labels = {
            'name': '分類名稱',
        }
        
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # [修改 1] 在 fields 列表中加入 'category'
        fields = ['category', 'image', 'name', 'price', 'stock', 'description']
        
        widgets = {
            # [修改 2] 加入 category 的選單樣式，使用 Bootstrap 的 form-select
            'category': forms.Select(attrs={'class': 'form-select'}),
            
            'name': forms.TextInput(attrs={'class': 'form-control dark-input', 'placeholder': '請輸入商品名稱'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'description': forms.Textarea(attrs={
                'class': 'form-control dark-input',  # <--- 這裡多加一個名字
                'rows': 3, 
                'placeholder': '商品描述...'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            # [修改 3] 加入 category 的中文標籤
            'category': '商品分類',
            'name': '商品名稱',
            'price': '價格',
            'stock': '庫存數量',
            'description': '商品描述',
            'image': '商品圖片',
        }