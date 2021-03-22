from django import forms



class ServiceBaseForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['api_key'].widget = forms.PasswordInput(
            attrs={
                'class': 'form-control'
            })

        self.fields['password'].widget = forms.PasswordInput(
            attrs={
                'class': 'form-control'
            })
