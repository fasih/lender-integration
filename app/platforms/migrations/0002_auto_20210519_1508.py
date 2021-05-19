# Generated by Django 3.1.8 on 2021-05-19 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platforms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanmanagementsystemapi',
            name='process_status_logic',
            field=models.TextField(blank=True, null=True, verbose_name='Process Status Logic'),
        ),
        migrations.AddField(
            model_name='platformserviceapi',
            name='process_status_logic',
            field=models.TextField(blank=True, null=True, verbose_name='Process Status Logic'),
        ),
        migrations.AlterField(
            model_name='loanmanagementsystemapi',
            name='iterable',
            field=models.BooleanField(blank=True, default=False, help_text='Yes if the API is going to be called                             multiple times then also configure Iterable Data                             Settings', null=True, verbose_name='Iterable'),
        ),
        migrations.AlterField(
            model_name='loanmanagementsystemapi',
            name='priority',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Priority'),
        ),
        migrations.AlterField(
            model_name='platformserviceapi',
            name='iterable',
            field=models.BooleanField(blank=True, default=False, help_text='Yes if the API is going to be called                             multiple times then also configure Iterable Data                             Settings', null=True, verbose_name='Iterable'),
        ),
        migrations.AlterField(
            model_name='platformserviceapi',
            name='priority',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Priority'),
        ),
    ]