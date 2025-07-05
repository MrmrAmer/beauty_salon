from django.db import models
import re

class UserLevel(models.Model):
    level_name = models.CharField(max_length=45)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.level_name


class UserManager(models.Manager):
    def basic_validator(self, postData):
        errors = {}

        if len(postData['first_name']) < 2 or not postData['first_name'].isalpha():
            errors['first_name'] = "First name must be at least 2 characters and letters only"

        if len(postData['last_name']) < 2 or not postData['last_name'].isalpha():
            errors['last_name'] = "Last name must be at least 2 characters and letters only"

        EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$")
        if not EMAIL_REGEX.match(postData['email']):
            errors['email'] = "Invalid email format"
        elif User.objects.filter(email=postData['email']).exists():
            errors['email'] = "Email already registered"

        if len(postData['password']) < 8:
            errors['password'] = "Password must be at least 8 characters"
        if postData['password'] != postData['confirm']:
            errors['confirm'] = "Passwords do not match"

        PHONE_REGEX = r'^\+?\d{10,15}$'
        if not re.match(PHONE_REGEX, postData.get('phone', '')):
            errors['phone'] = "Enter a valid phone number."

        return errors


class User(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=80)
    user_level = models.ForeignKey(UserLevel, on_delete=models.CASCADE, related_name='users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"