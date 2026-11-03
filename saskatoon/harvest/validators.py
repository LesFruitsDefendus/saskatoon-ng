from django.core.validators import FileExtensionValidator

IMAGE_VALIDATORS = [FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
