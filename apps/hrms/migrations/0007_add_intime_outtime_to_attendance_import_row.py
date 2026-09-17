from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hrms", "0006_attendanceimport_month_attendanceimport_year"),
    ]

    operations = [
        migrations.AddField(
            model_name="attendanceimportrow",
            name="InTime",
            field=models.DateTimeField(
                null=True,
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="attendanceimportrow",
            name="OutTime",
            field=models.DateTimeField(
                null=True,
                blank=True,
            ),
        ),
    ]