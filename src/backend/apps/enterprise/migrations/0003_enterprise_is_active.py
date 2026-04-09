from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("enterprise", "0002_masterdata"),
    ]

    operations = [
        migrations.AddField(
            model_name="enterprise",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="是否启用"),
        ),
    ]
