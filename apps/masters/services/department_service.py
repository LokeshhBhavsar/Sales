from django.db import transaction

from apps.masters.models.department import Department


class DepartmentService:

    @staticmethod
    @transaction.atomic
    def create_department(data):

        return Department.objects.create(
            **data
        )

    @staticmethod
    def get_all_departments():

        return Department.objects.select_related(
            "plant",
            "plant__company"
        ).all()

    @staticmethod
    def get_department(department_id):

        return Department.objects.select_related(
            "plant",
            "plant__company"
        ).get(
            id=department_id
        )

    @staticmethod
    @transaction.atomic
    def update_department(department, data):

        for field, value in data.items():

            setattr(
                department,
                field,
                value
            )

        department.save()

        return department

    @staticmethod
    @transaction.atomic
    def delete_department(department):

        department.delete()