# Generated by Django 3.2.12 on 2025-04-25 18:29

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_ckeditor_5.fields
import imagekit.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Artifact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', django_ckeditor_5.fields.CKEditor5Field(blank=True)),
                ('image', imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to='artifacts/')),
                ('thumbnail', imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to='artifacts/thumbnails/')),
                ('popularity_score', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, help_text='Tell others about yourself')),
                ('website', models.URLField(blank=True)),
                ('avatar', imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to='avatars/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('blocked_categories', models.ManyToManyField(blank=True, related_name='blocked_by', to='artifacts.Category')),
                ('blocked_tags', models.ManyToManyField(blank=True, related_name='blocked_by', to='artifacts.Tag')),
                ('blocked_users', models.ManyToManyField(blank=True, related_name='blocked_by', to=settings.AUTH_USER_MODEL)),
                ('following', models.ManyToManyField(blank=True, related_name='followers', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='preferences', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', django_ckeditor_5.fields.CKEditor5Field(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('artifact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='artifacts.artifact')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='artifact',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='artifacts', to='artifacts.category'),
        ),
        migrations.AddField(
            model_name='artifact',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='artifacts', to='artifacts.Tag'),
        ),
        migrations.AddField(
            model_name='artifact',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='artifacts', to=settings.AUTH_USER_MODEL),
        ),
    ]
