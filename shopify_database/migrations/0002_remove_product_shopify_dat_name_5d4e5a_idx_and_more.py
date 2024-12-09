# Generated by Django 5.1.3 on 2024-12-08 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify_database', '0001_initial'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='product',
            name='shopify_dat_name_5d4e5a_idx',
        ),
        migrations.RemoveField(
            model_name='product',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='product',
            name='name',
        ),
        migrations.RemoveField(
            model_name='product',
            name='pipeline',
        ),
        migrations.AddField(
            model_name='product',
            name='city',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='country',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='image_url',
            field=models.URLField(blank=True, default='', null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='niche',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='title',
            field=models.CharField(blank=True, default='No title', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['title'], name='shopify_dat_title_9b9efb_idx'),
        ),
    ]