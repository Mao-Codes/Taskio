from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        FREELANCER = "freelancer", "Freelancer"
        CLIENT = "client", "Client"

    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.FREELANCER
    )

    @property
    def is_freelancer(self):
        return self.role == self.Role.FREELANCER

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT