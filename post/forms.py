from django.forms import ModelForm
from .models import Post

class FileUploadForm(ModelForm):
    class Meta:
        model = Post
        fields = ['id', 'title', 'file', 'content']