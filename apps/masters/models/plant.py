import uuid

from django.db import models

from .company import Company


class Plant(models.Model):
     id = models.UUIDField(
          primary_key=True,
         default=uuid.uuid4,
         editable=False

     ) 
     company = models.ForeignKey(
          Company,
          on_delete=models.PROTECT,
          related_name="plants"
     )
     name = models.CharField(
      max_length=255,
      unique=True
     )
     location = models.CharField(
          max_length=100,
          blank=True,
          null=True
     )
     is_active = models.BooleanField(
          default=True
     )
     created_at = models.DateTimeField(
            auto_now_add=True
     )
     updated_at = models.DateTimeField(
             auto_now = True
     )

     class Meta:
          db_table = "plants"
          ordering = ['name']

          constraints = [
               models.UniqueConstraint(
                    fields = ["company","name"],
                    name = "unique_plant_name_per_company"
               )
          ]
    
def __str__(self):
         return self.name

