from django.db import models
from nomadgram.users import models as user_models

# Create your models here.
class TimeStampedModel(models.Model) :

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta :
        abstract = True


class Image(TimeStampedModel) :

    file = models.ImageField()
    location = models.CharField(max_length = 140)
    captions = models.TextField()
    creator = models.ForeignKey(user_models.User, null=True, on_delete=models.CASCADE)

class Comment(TimeStampedModel) :

    message = models.TextField()
    creator = models.ForeignKey(user_models.User, null=True, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, null=True, on_delete=models.CASCADE)


class Like(TimeStampedModel) :

    creator = models.ForeignKey(user_models.User, null=True, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, null=True, on_delete=models.CASCADE)
