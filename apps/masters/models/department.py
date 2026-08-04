import uuid

from django.db import models

from .plant import Plant


class Department(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=True
    )
    plant = models.ForeignKey(
        Plant,
        on_delete= models.CASCADE,
        related_name="departments"

    )
    name = models.CharField(
        max_length=255

    )
    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add = True
    )

    updated_at = models.DateField(
        auto_now = True
    ) 

    class MEta :
        db_table = "departments"
        ordering = ['name']

        constraints= [
            models.UniqueConstraint(
                fields = ["plant","name"],
                name = "unique_department_name_per_plant"
            )
        ]

        def __str__(self):
            return self.name

        