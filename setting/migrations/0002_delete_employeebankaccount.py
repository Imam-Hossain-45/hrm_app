from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('setting', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='EmployeeBankAccount',
        ),
    ]
