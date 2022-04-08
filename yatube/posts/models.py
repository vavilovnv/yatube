from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        '''При ревью было сформулировано такое замечание:
        Можно добавить еще какой-нибудь префикс Group_,
        чтобы понимать, что это относится к группам.

        Только это замечание не получилось обработать.
        Если я его верно понял, нужно название свойства
        title заменить на group_title? Пробовал так сделать,
        но не получается пройти автотесты. Ожидается именно title.
        '''
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-pub_date']
