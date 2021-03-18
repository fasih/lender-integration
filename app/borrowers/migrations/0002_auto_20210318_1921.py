# Generated by Django 3.1.7 on 2021-03-18 19:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('platforms', '0001_initial'),
        ('lenders', '0001_initial'),
        ('borrowers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanapplicationdata',
            name='lms_api',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='platforms.loanmanagementsystemapi', verbose_name='LMS API'),
        ),
        migrations.AddField(
            model_name='loanapplicationdata',
            name='svc_api',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='platforms.platformserviceapi', verbose_name='SVC API'),
        ),
        migrations.AddField(
            model_name='loanapplication',
            name='cp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='platforms.channelpartners', verbose_name='Channel Partner'),
        ),
        migrations.AddField(
            model_name='loanapplication',
            name='lender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='lenders.lendersystem', verbose_name='Lender'),
        ),
        migrations.AddField(
            model_name='loanapplication',
            name='lms',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='platforms.loanmanagementsystem', verbose_name='LMS'),
        ),
        migrations.AddField(
            model_name='loanapplication',
            name='svc',
            field=models.ManyToManyField(blank=True, to='platforms.PlatformService', verbose_name='Services'),
        ),
        migrations.AlterUniqueTogether(
            name='loanapplication',
            unique_together={('lms', 'lmsid')},
        ),
    ]