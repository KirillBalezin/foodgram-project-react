from recipes.models import Ingredient
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, **options):
        with open("ingredients.csv") as file:
            for line in file:
                ingredient = line.split(',')
                Ingredient.objects.get_or_create(
                    name=ingredient[0],
                    measurement_unit=ingredient[1]
                )
        self.stdout.write(self.style.SUCCESS('Все данные загружены.'))
