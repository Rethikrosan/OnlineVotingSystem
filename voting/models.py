from django.db import models


class Student(models.Model):
    roll_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    has_voted = models.BooleanField(default=False)

    def __str__(self):
        return self.roll_number


class Candidate(models.Model):
    POSITION_CHOICES = [
    ("President", "President"),
    ("Vice President", "Vice President"),
    ("Secretary", "Secretary"),
    ("Joint Secretary", "Joint Secretary"),
    ("Treasurer", "Treasurer"),
    ("Cultural", "Cultural"),
    ("Sports", "Sports"),
    ("Placement", "Placement"),
    ("Brand Ambassador", "Brand Ambassador"),
]
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    photo = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} - {self.position}"


class Vote(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    position = models.CharField(max_length=50)
    voted_at = models.DateTimeField(auto_now_add=True)


class Election(models.Model):
    is_active = models.BooleanField(default=False)