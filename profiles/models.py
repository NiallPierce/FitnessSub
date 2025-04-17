from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
import os

def user_profile_picture_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/profile_pictures/<filename>
    return f'user_{instance.user.id}/profile_pictures/{filename}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    address_line_1 = models.CharField(max_length=50, blank=True)
    address_line_2 = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    newsletter_subscription = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to=user_profile_picture_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        # If profile picture is being updated
        if self.profile_picture:
            try:
                # Open the image
                img = Image.open(self.profile_picture)
                
                # Resize the image to 300x300
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    
                    # Save the resized image
                    temp_file = ContentFile(b'')
                    img.save(temp_file, format=img.format)
                    temp_file.seek(0)
                    
                    # Save the resized image to the profile_picture field
                    self.profile_picture.save(
                        os.path.basename(self.profile_picture.name),
                        temp_file,
                        save=False
                    )
            except Exception as e:
                # If there's an error processing the image, just save the original
                pass
                
        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile
    """
    if created:
        UserProfile.objects.create(user=instance)
    # Existing users: just save the profile
    instance.userprofile.save()