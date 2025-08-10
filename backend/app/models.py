from django.db import models

# Create your models here.


class Test(models.Model):
    """
    A simple test model to verify database connectivity.
    """
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name