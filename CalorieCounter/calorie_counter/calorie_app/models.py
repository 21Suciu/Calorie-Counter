from django.db import models


class FoodLog(models.Model):
    food_name = models.CharField(max_length=200)
    calories = models.FloatField()
    portion_size = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField(auto_now_add=True)  # DateField instead of DateTimeField

    def __str__(self):
        return f"{self.food_name} - {self.calories} kcal"
