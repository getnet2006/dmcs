from django.db import models
from account.models import User
from documents.models import Document


# Create your models here.
class Consumer(models.Model):
    CONSUMER_TYPES = (
        ("External", "External"),
        ("Internal", "Internal"),
    )

    name = models.CharField(max_length=255)
    owner_work_unit = models.CharField(max_length=255)
    purpose_of_usage = models.TextField()
    consumer_type = models.CharField(max_length=20, choices=CONSUMER_TYPES)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ConsumerOnboardingStage(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Application(models.Model):
    name = models.CharField(max_length=255)
    consumer = models.ForeignKey(
        Consumer, on_delete=models.CASCADE, related_name="applications"
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    current_stage = models.ForeignKey(
        ConsumerOnboardingStage, on_delete=models.SET_NULL, null=True
    )
    source_ip = models.GenericIPAddressField()
    description = models.TextField(blank=True)
    last_stage_updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ApplicationDocument(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)


class ApplicationSubscription(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    subscription = models.CharField(
        max_length=255
    )  # models.ForeignKey(Subscription, on_delete=models.CASCADE)


class ConsumerCommunication(models.Model):
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="communications"
    )
    remark = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
