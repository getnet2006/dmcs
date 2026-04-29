from django.db import models
from django.utils import timezone
from account.models import User
from documents.models import Document


class Subscription(models.Model):
    # authentication options: API Key, OAuth, JWT, etc.
    AUTHENTICATION_TYPES = [
        ("api_key", "API Key"),
        ("oauth", "OAuth"),
        ("jwt", "JWT"),
    ]
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscriptions"
    )
    authentication_type = models.CharField(max_length=100, choices=AUTHENTICATION_TYPES)
    client_id = models.CharField(max_length=255, unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class Consumer(models.Model):
    CONSUMER_TYPES = (
        ("External", "External"),
        ("Internal", "Internal"),
    )

    name = models.CharField(max_length=255)
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
    document_category = models.CharField(max_length=255, blank=True)

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
    documents = models.ManyToManyField(
        Document, blank=True, related_name="applications"
    )
    subscriptions = models.ManyToManyField(
        Subscription, blank=True, related_name="applications"
    )
    owner_work_unit = models.CharField(max_length=255)
    purpose_of_usage = models.TextField()
    source_ip = models.GenericIPAddressField()
    last_stage_updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def set_stage(self, stage):
        """Sets the current stage and updates the timestamp."""
        if self.current_stage != stage:
            self.current_stage = stage
            self.last_stage_updated_at = timezone.now()
            self.save(update_fields=["current_stage", "last_stage_updated_at"])

    def transition_by_document(self, document):
        """Attempts to transition to a new stage based on a document's category."""
        new_stage = ConsumerOnboardingStage.objects.filter(
            document_category=document.category.name
        ).first()
        if new_stage:
            self.set_stage(new_stage)
            return True
        return False

    def save(self, *args, **kwargs):
        if not self.pk:
            # Set initial stage for new applications if not already set
            if not self.current_stage:
                self.current_stage = ConsumerOnboardingStage.objects.order_by(
                    "order"
                ).first()
        else:
            # Detect stage change for existing applications
            # We use a simple query to get the old value
            try:
                old_instance = Application.objects.get(pk=self.pk)
                if old_instance.current_stage != self.current_stage:
                    self.last_stage_updated_at = timezone.now()
            except Application.DoesNotExist:
                pass

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]
        permissions = [
            ("add_document_to_application", "Can add document to application"),
            ("add_subscription_to_application", "Can add subscription to application"),
        ]


class ConsumerCommunication(models.Model):
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="communications"
    )
    remark = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
