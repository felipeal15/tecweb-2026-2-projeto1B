from django.db import models

# Create your models here.

class Tag(models.Model):
    # unique=True garante no próprio banco que não existam tags duplicadas
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.id}. {self.name}"


class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(null=True)
    # Many-to-One: várias anotações podem ter a mesma tag, e cada anotação
    # tem no máximo uma. Se a tag for apagada, a anotação só fica sem tag.
    tag = models.ForeignKey(
        Tag,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notes',
    )

    def __str__(self):
        return f"{self.id}. {self.title}"
