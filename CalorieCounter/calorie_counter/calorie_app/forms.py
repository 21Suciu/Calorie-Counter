from django import forms


class FoodLogForm(forms.Form):
    food_name = forms.CharField(max_length=255)
    calories = forms.FloatField()
    portion_size = forms.CharField(max_length=100, required=False)

