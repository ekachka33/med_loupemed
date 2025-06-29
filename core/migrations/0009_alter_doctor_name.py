# core/migrations/0009_alter_doctor_name.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_doctor_options_remove_doctor_full_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='name',
            field=models.CharField(default='', max_length=255, verbose_name='Полное имя'), # <-- ВОТ ЭТО ДОБАВЛЕНО
            preserve_default=False,
        ),
    ]