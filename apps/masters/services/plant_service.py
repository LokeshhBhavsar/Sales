from django.db import transaction

from apps.masters.models.plant import Plant


class PlantService:

    @staticmethod
    @transaction.atomic
    def create_plant(data):

        return Plant.objects.create(
            **data
        )


    @staticmethod
    def get_all_plants():

        return Plant.objects.select_related(
            "company"
        ).all()


    @staticmethod
    def get_plant(plant_id):

        return Plant.objects.select_related(
            "company"
        ).get(
            id=plant_id
        )


    @staticmethod
    @transaction.atomic
    def update_plant(plant, data):

        for field, value in data.items():
            setattr(
                plant,
                field,
                value
            )

        plant.save()

        return plant


    @staticmethod
    @transaction.atomic
    def delete_plant(plant):

        plant.delete()