# Generated by Django 5.0.6 on 2024-06-29 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dispatch', '0003_alter_medication_code_alter_medication_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medication',
            name='image',
            field=models.ImageField(upload_to='media/'),
        ),
    ]
