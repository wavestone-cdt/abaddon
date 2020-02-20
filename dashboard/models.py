from django.db import models

# Create your models here.
"""
sqlitebrowser db.sqlite3
python3 manage.py shell
from dashboard.models import Techniques
technique1 = Techniques(name="DLL hijacking", used=1)
technique1.publish()
"""

class Techniques(models.Model):
    name = models.CharField(max_length=50)
    #text = models.TextField()
    #created_date = models.DateTimeField(default=timezone.now)
    used = models.BooleanField(default=False)

    def publish(self):
        #self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name