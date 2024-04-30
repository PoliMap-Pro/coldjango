# Generated by Django 4.2.11 on 2024-04-30 22:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jacobsladder', '0008_floorcode_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ballot_position', models.PositiveSmallIntegerField(default=0)),
            ],
        ),
        migrations.AlterField(
            model_name='senategroup',
            name='abbreviation',
            field=models.CharField(max_length=15),
        ),
        migrations.AlterField(
            model_name='senategroup',
            name='name',
            field=models.CharField(blank=True, max_length=63, null=True),
        ),
        migrations.AddConstraint(
            model_name='contention',
            constraint=models.UniqueConstraint(fields=('seat', 'candidate', 'election'), name='unique_seat_candidate_election'),
        ),
        migrations.AddField(
            model_name='stand',
            name='candidate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jacobsladder.senatecandidate'),
        ),
        migrations.AddField(
            model_name='stand',
            name='election',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jacobsladder.senateelection'),
        ),
        migrations.AddConstraint(
            model_name='stand',
            constraint=models.UniqueConstraint(fields=('candidate', 'election'), name='candidate_election'),
        ),
    ]
