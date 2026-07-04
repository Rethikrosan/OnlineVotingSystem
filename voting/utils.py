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

        if not Student.objects.filter(roll_number=roll).exists():
            Student.objects.create(
                roll_number=roll,
                name=name,
                password=make_password(dob)
            )
            count += 1

    return count