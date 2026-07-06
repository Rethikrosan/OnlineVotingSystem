from openpyxl import load_workbook
from django.contrib.auth.hashers import make_password
from .models import Student


def import_students(file):

    workbook = load_workbook(file, read_only=True)
    sheet = workbook.active

    students_to_create = []
    count = 0

    for row in sheet.iter_rows(min_row=2, values_only=True):

        if not row[0]:
            continue

        roll = str(row[0]).strip()
        name = str(row[1]).strip()
        password = str(row[2]).strip()

        students_to_create.append(
            Student(
                roll_number=roll,
                name=name,
                password=make_password(password)
            )
        )

        count += 1

    Student.objects.bulk_create(
        students_to_create,
        ignore_conflicts=True
    )

    return count