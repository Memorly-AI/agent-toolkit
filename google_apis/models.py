from django.db import models


class GoogleCredential(models.Model):
    uuid = models.CharField(max_length=255, null=True, blank=True)
    credential = models.JSONField(default=dict, null=True)
    
    def __str__(self):
        return f'{self.uuid}'
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'credential': self.credential
        }
