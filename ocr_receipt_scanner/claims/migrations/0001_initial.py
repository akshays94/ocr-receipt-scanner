# Generated by Django 2.0.9 on 2018-11-19 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ReceiptScan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('corpus', models.TextField()),
                ('receipt_no_tags', models.TextField()),
                ('receipt_amt_tags', models.TextField()),
                ('receipt_data', models.TextField()),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
