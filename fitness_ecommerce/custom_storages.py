from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
import logging

logger = logging.getLogger(__name__)

class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION
    file_overwrite = True
    object_parameters = {
        'CacheControl': 'max-age=86400',
    }
    
    def _save(self, name, content):
        logger.info(f"Attempting to save static file: {name}")
        try:
            # Force upload by setting modified time to now
            content.modified = True
            result = super()._save(name, content)
            logger.info(f"Successfully saved static file: {name}")
            return result
        except Exception as e:
            logger.error(f"Error saving static file {name}: {str(e)}")
            raise

class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION
    file_overwrite = True
    object_parameters = {
        'CacheControl': 'max-age=86400',
    }
    custom_domain = f'{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    
    def _save(self, name, content):
        logger.info(f"Attempting to save media file: {name}")
        try:
            # Force upload by setting modified time to now
            content.modified = True
            result = super()._save(name, content)
            logger.info(f"Successfully saved media file: {name}")
            return result
        except Exception as e:
            logger.error(f"Error saving media file {name}: {str(e)}")
            raise 