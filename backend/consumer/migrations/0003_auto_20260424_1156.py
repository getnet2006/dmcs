from django.db import migrations


def create_onboarding_stages(apps, schema_editor):
    # Fetch the model via the apps registry (don't import it directly!)
    ConsumerOnboardingStage = apps.get_model("consumer", "ConsumerOnboardingStage")

    stages = [
        ConsumerOnboardingStage(
            id=1,
            name="Onboarding",
            order=1,
            document_category="Onboarding",
        ),
        ConsumerOnboardingStage(
            id=2, name="BRD submission", order=2, document_category="BRD"
        ),
        ConsumerOnboardingStage(
            id=3,
            name="Certificate submission",
            order=3,
            document_category="Certificate",
        ),
        ConsumerOnboardingStage(
            id=4,
            name="API Documentation Submission",
            order=4,
            document_category="API Documentation",
        ),
        ConsumerOnboardingStage(
            id=5,
            name="UAT Signoff Submission",
            order=5,
            document_category="UAT Signoff",
        ),
    ]

    ConsumerOnboardingStage.objects.bulk_create(stages)


def remove_onboarding_stages(apps, schema_editor):
    ConsumerOnboardingStage = apps.get_model("consumer", "ConsumerOnboardingStage")
    ConsumerOnboardingStage.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        (
            "consumer",
            "0001_initial",
        ),
    ]

    operations = [
        migrations.RunPython(
            create_onboarding_stages, reverse_code=remove_onboarding_stages
        ),
    ]
