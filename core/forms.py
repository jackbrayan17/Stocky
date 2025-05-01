from django import forms
from .models import Product
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Store, Suggestion

class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ['message', 'name', 'whatsapp_number']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'rows': 4, 'placeholder': 'Entrez votre suggestion ici...'}),
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Votre nom (optionnel)'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Numéro WhatsApp (optionnel)'}),
        }
        labels = {
            'message': 'Suggestion',
            'name': 'Nom',
            'whatsapp_number': 'Numéro WhatsApp',
        }
class OrderItemForm(forms.Form):
    client_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Customer Name'})
    )
    client_phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Phone Number'})
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.none(),
        widget=forms.Select(attrs={'class': 'w-full p-2 border rounded'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'})
    )

    def __init__(self, *args, store=None, **kwargs):
        super().__init__(*args, **kwargs)
        if store:
            self.fields['product'].queryset = Product.objects.filter(store=store)


from django import forms
from .models import Product, Category

from django import forms
from .models import Product, Category

class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'quantity', 'alert_threshold', 'category']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'alert_threshold': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class UpdateProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'quantity', 'alert_threshold', 'category']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'alert_threshold': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    # You can add validation similar to the AddProductForm
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError('Price must be greater than zero.')
        return price
    
class ManagerRegistrationForm(UserCreationForm):
    store = forms.ModelChoiceField(queryset=Store.objects.all(), empty_label="Select Store", required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'store']

class CreateOrderForm(forms.Form):
    client_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Client Name'}))
    client_phone = forms.CharField(max_length=15, widget = forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': ' Client Number'}))

    def __init__(self, store, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically add product fields
        products = Product.objects.filter(store=store)
        for product in products:
            self.fields[f'quantity_{product.id}'] = forms.IntegerField(
                required=False, min_value=0, initial=0,
                label=f'{product.name} (Stock: {product.quantity})'
            )

    # You can also add validation to check if stock is enough
    def clean(self):
        cleaned_data = super().clean()
        products = Product.objects.filter(store=self.store)
        for product in products:
            quantity = cleaned_data.get(f'quantity_{product.id}')
            if quantity and product.quantity < quantity:
                self.add_error(f'quantity_{product.id}', f'Not enough stock for {product.name}.')
        return cleaned_data