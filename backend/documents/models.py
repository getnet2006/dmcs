from django.db import models

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    # Using IntegerField instead of a formal ForeignKey
    user_id = models.IntegerField(null=True, blank=True) 
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Document(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    document_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    file_size = models.BigIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    version = models.CharField(max_length=20)
    approval_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    
    # Simple integer IDs for User and Entity
    user_id = models.IntegerField(null=True, blank=True) # Created by
    related_entity_id = models.IntegerField()            # App or API ID
    
    file_location = models.FileField(upload_to='documents/') 
    
    created_date = models.DateTimeField(auto_now_add=True)
    approved_by = models.IntegerField(null=True, blank=True) # User ID of approver
    approved_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name