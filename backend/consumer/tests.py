from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Consumer, Application, ConsumerOnboardingStage, Subscription
from documents.models import Document, Category
from datetime import timedelta

User = get_user_model()

class ApplicationStageTransitionTest(TestCase):
    def setUp(self):
        # Clear existing stages created by migrations
        ConsumerOnboardingStage.objects.all().delete()
        
        self.user = User.objects.create_user(username="testuser", password="password")
        self.consumer = Consumer.objects.create(
            name="Test Consumer",
            owner_work_unit="IT",
            purpose_of_usage="Testing",
            consumer_type="Internal",
            email="test@example.com",
            phone="1234567890",
            created_by=self.user
        )
        
        # Create stages
        self.stage1 = ConsumerOnboardingStage.objects.create(name="Stage 1", order=1, document_category="Cat1")
        self.stage2 = ConsumerOnboardingStage.objects.create(name="Stage 2", order=2, document_category="Cat2")
        
        # Create document category
        self.category1 = Category.objects.create(name="Cat1")
        self.category2 = Category.objects.create(name="Cat2")
        
        # Create a document
        self.doc1 = Document.objects.create(
            name="Doc 1",
            file_type="pdf",
            file_size=1024,
            category=self.category1,
            version="1.0",
            related_entity_id=1
        )
        self.doc2 = Document.objects.create(
            name="Doc 2",
            file_type="pdf",
            file_size=1024,
            category=self.category2,
            version="1.0",
            related_entity_id=1
        )

    def test_initial_stage_assignment(self):
        """Test that a new application is assigned the first stage automatically on save."""
        app = Application.objects.create(
            name="Test App",
            consumer=self.consumer,
            user=self.user,
            source_ip="127.0.0.1"
        )
        self.assertEqual(app.current_stage, self.stage1)

    def test_stage_change_updates_timestamp(self):
        """Test that updating current_stage manually updates last_stage_updated_at."""
        app = Application.objects.create(
            name="Test App",
            consumer=self.consumer,
            user=self.user,
            source_ip="127.0.0.1",
            current_stage=self.stage1
        )
        # Mocking last_stage_updated_at to a past time
        past_time = timezone.now() - timedelta(days=1)
        Application.objects.filter(pk=app.pk).update(last_stage_updated_at=past_time)
        app.refresh_from_db()
        
        initial_timestamp = app.last_stage_updated_at
        
        # Manually update stage
        app.current_stage = self.stage2
        app.save()
        
        # Re-fetch from DB
        app.refresh_from_db()
        
        self.assertNotEqual(app.last_stage_updated_at, initial_timestamp)
        self.assertGreater(app.last_stage_updated_at, initial_timestamp)

    def test_transition_by_document(self):
        """Test transitioning to a new stage via document category."""
        app = Application.objects.create(
            name="Test App",
            consumer=self.consumer,
            user=self.user,
            source_ip="127.0.0.1",
            current_stage=self.stage1
        )
        
        success = app.transition_by_document(self.doc2)
        
        self.assertTrue(success)
        self.assertEqual(app.current_stage, self.stage2)
        self.assertIsNotNone(app.last_stage_updated_at)

    def test_set_stage_method(self):
        """Test set_stage method updates correctly."""
        app = Application.objects.create(
            name="Test App",
            consumer=self.consumer,
            user=self.user,
            source_ip="127.0.0.1",
            current_stage=self.stage1
        )
        
        app.set_stage(self.stage2)
        
        app.refresh_from_db()
        self.assertEqual(app.current_stage, self.stage2)
        self.assertIsNotNone(app.last_stage_updated_at)
