import pandas as pd
from django.contrib.auth.hashers import make_password
from .models import Student


def import_students(file):
    df = pd.read_excel(file)
    count = 0

    for _, row in df.iterrows():
        roll = str(row["Roll Number"])
        name = str(row["Name"])
        dob = str(row["DOB"])

        Student.objects.update_or_create(
            roll_number=roll,
            defaults={
                "name": name,
                "password": make_password(dob),
            }
        )

        count += 1

    return count