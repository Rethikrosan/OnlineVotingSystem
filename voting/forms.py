from django import forms


class StudentLoginForm(forms.Form):
    roll_number = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField()


class CandidateForm(forms.Form):
    name = forms.CharField()
    position = forms.ChoiceField(
    choices=[
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
    )
    photo = forms.ImageField()