from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('image', models.ImageField(
                    blank=True,
                    null=True,
                    upload_to='achievements/%Y/%m/%d/'
                )),
                ('date_achieved', models.DateTimeField(auto_now_add=True)),
                ('points', models.IntegerField(default=0)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='achievements',
                    to='auth.user'
                )),
            ],
        ),
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('badge_type', models.CharField(
                    choices=[
                        ('workout', 'Workout'),
                        ('nutrition', 'Nutrition'),
                        ('community', 'Community'),
                        ('streak', 'Streak')
                    ],
                    max_length=20
                )),
                ('image', models.ImageField(upload_to='badges/%Y/%m/%d/')),
                ('required_points', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('points', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='GroupWorkout',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('workout_type', models.CharField(
                    choices=[
                        ('virtual', 'Virtual'),
                        ('local', 'Local')
                    ],
                    max_length=20
                )),
                ('date_time', models.DateTimeField()),
                ('duration', models.IntegerField(
                    help_text='Duration in minutes'
                )),
                ('max_participants', models.IntegerField()),
                ('location', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True
                )),
                ('meeting_link', models.URLField(blank=True, null=True)),
                ('created_by', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='created_workouts',
                    to='auth.user'
                )),
                ('participants', models.ManyToManyField(
                    related_name='group_workouts',
                    to='auth.user'
                )),
            ],
        ),
        migrations.CreateModel(
            name='SocialPost',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('content', models.TextField()),
                ('image', models.ImageField(
                    blank=True,
                    null=True,
                    upload_to='social_posts/%Y/%m/%d/'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('likes', models.ManyToManyField(
                    blank=True,
                    related_name='liked_posts',
                    to='auth.user'
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='social_posts',
                    to='auth.user'
                )),
            ],
        ),
        migrations.CreateModel(
            name='UserBadge',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('date_earned', models.DateTimeField(auto_now_add=True)),
                ('badge', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='community.badge'
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='user_badges',
                    to='auth.user'
                )),
            ],
            options={
                'unique_together': {('user', 'badge')},
            },
        ),
        migrations.CreateModel(
            name='ProgressEntry',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('entry_type', models.CharField(
                    choices=[
                        ('workout', 'Workout'),
                        ('nutrition', 'Nutrition'),
                        ('measurement', 'Measurement'),
                        ('goal', 'Goal')
                    ],
                    max_length=20
                )),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('value', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    max_digits=10,
                    null=True
                )),
                ('unit', models.CharField(
                    blank=True,
                    max_length=20,
                    null=True
                )),
                ('date', models.DateTimeField(default=timezone.now)),
                ('image', models.ImageField(
                    blank=True,
                    null=True,
                    upload_to='progress_images/%Y/%m/%d/'
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='progress_entries',
                    to='auth.user'
                )),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('post', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='comments',
                    to='community.socialpost'
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='auth.user'
                )),
            ],
        ),
        migrations.CreateModel(
            name='ChallengeParticipation',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('joined_date', models.DateTimeField(auto_now_add=True)),
                ('completed', models.BooleanField(default=False)),
                ('completion_date', models.DateTimeField(
                    blank=True,
                    null=True
                )),
                ('challenge', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='community.challenge'
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='auth.user'
                )),
            ],
            options={
                'unique_together': {('user', 'challenge')},
            },
        ),
        migrations.AddField(
            model_name='challenge',
            name='participants',
            field=models.ManyToManyField(
                through='community.ChallengeParticipation',
                to='auth.user'
            ),
        ),
    ]
