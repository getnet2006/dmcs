from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Document
from .serializers import DocumentSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows documents to be viewed or edited.
    """
    queryset = Document.objects.all().order_by('-created_date')
    serializer_class = DocumentSerializer
    
    # MultiPartParser is required for React to upload physical files
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        """
        Overrides the create method to automatically save 
        the user who uploaded the document.
        """
        # This assumes the React dev sends an Auth Token. 
        # If not authenticated, it will save as None or you can handle an error.
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()