from django.db import models

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Аватарка")
    
    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Профіль користувача"
        verbose_name_plural = "Профілі користувачів"

    points_earned = models.IntegerField(default=0)
    response_time = models.DurationField(null=True, blank=True)
    role = models.CharField(max_length=50, blank=True, verbose_name="Роль користувача")
    class Admin:
        pass
    
    

