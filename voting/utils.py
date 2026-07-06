from openpyxl import load_workbook
from django.contrib.auth.hashers import make_password
from .models import Student


def import_students(file):

    workbook = load_workbook(file, read_only=True)
    sheet = workbook.active

    count = 0

    for row in sheet.iter_rows(min_row=2, values_only=True):

        if not row[0]:
            continue

        roll = str(row[0]).strip()
        name = str(row[1]).strip()
        password = str(row[2]).strip()

        Student.objects.update_or_create(
            roll_number=roll,
            defaults={
                "name": name,
                "password": make_password(password),
            },
        )

        count += 1

    return count