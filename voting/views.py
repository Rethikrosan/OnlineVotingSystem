
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.db.models import Count

from .models import Student, Candidate, Election, Vote
from .forms import ExcelUploadForm, CandidateForm
from .utils import import_students


# ===========================
# HOME
# ===========================

def home(request):
    return render(request, "home/home.html")


# ===========================
# STUDENT LOGIN
# ===========================

def student_login(request):

    if request.method == "POST":

        roll = request.POST.get("roll_number")
        password = request.POST.get("password")

        try:
            student = Student.objects.get(roll_number=roll)

            if check_password(password, student.password):
                request.session["student_id"] = student.id
                request.session["votes"] = {}
                return redirect("election_guidelines")

            else:
                messages.error(request, "Invalid Password")

        except Student.DoesNotExist:
            messages.error(request, "Invalid Roll Number")

    return render(request, "student/login.html")


# ===========================
# ADMIN LOGIN
# ===========================

def admin_login(request):

    if request.method == "POST":

        user = authenticate(
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )

        if user and user.is_superuser:
            login(request, user)
            return redirect("admin_dashboard")

        messages.error(request, "Invalid Credentials")

    return render(request, "admin_panel/login.html")


# ===========================
# ADMIN DASHBOARD
# ===========================

@login_required(login_url="admin_login")
def admin_dashboard(request):

    election = Election.objects.first()

    if election is None:
        election = Election.objects.create(is_active=False)

    total_students = Student.objects.count()
    voted_students = Student.objects.filter(has_voted=True).count()
    total_candidates = Candidate.objects.count()

    if total_students > 0:
        voting_percentage = round((voted_students / total_students) * 100, 2)
    else:
        voting_percentage = 0

    context = {
        "election": election,
        "total_students": total_students,
        "voted_students": voted_students,
        "total_candidates": total_candidates,
        "voting_percentage": voting_percentage,
    }

    return render(
        request,
        "admin_panel/dashboard.html",
        context
    )

# ===========================
# IMPORT STUDENTS
# ===========================

@login_required(login_url="admin_login")
def import_students_view(request):

    form = ExcelUploadForm()

    if request.method == "POST":

        form = ExcelUploadForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            total = import_students(
                request.FILES["excel_file"]
            )

            messages.success(
                request,
                f"{total} Students Imported Successfully."
            )

    return render(
        request,
        "admin_panel/import_students.html",
        {
            "form": form
        }
    )


# ===========================
# ADD CANDIDATE
# ===========================

@login_required(login_url="admin_login")
def add_candidate(request):

    form = CandidateForm()

    if request.method == "POST":

        form = CandidateForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            Candidate.objects.create(
                name=form.cleaned_data["name"],
                position=form.cleaned_data["position"],
                photo=form.cleaned_data["photo"]
            )

            messages.success(
                request,
                "Candidate Added Successfully."
            )

            return redirect("add_candidate")

    return render(
        request,
        "admin_panel/add_candidate.html",
        {
            "form": form
        }
    )


# ===========================
# VIEW CANDIDATES
# ===========================

@login_required(login_url="admin_login")
def candidate_list(request):

    candidates = Candidate.objects.all()

    return render(
        request,
        "admin_panel/candidate_list.html",
        {
            "candidates": candidates
        }
    )


# ===========================
# DELETE CANDIDATE
# ===========================

@login_required(login_url="admin_login")
def delete_candidate(request, id):

    candidate = get_object_or_404(
        Candidate,
        id=id
    )

    candidate.delete()

    messages.success(
        request,
        "Candidate Deleted Successfully."
    )

    return redirect("candidate_list")


# ===========================
# START ELECTION
# ===========================

@login_required(login_url="admin_login")
def start_election(request):

    election, created = Election.objects.get_or_create(id=1)

    election.is_active = True
    election.save()

    messages.success(
        request,
        "Election Started Successfully."
    )

    return redirect("admin_dashboard")


# ===========================
# END ELECTION
# ===========================

@login_required(login_url="admin_login")
def end_election(request):

    election, created = Election.objects.get_or_create(id=1)

    election.is_active = False
    election.save()

    messages.success(
        request,
        "Election Ended Successfully."
    )

    return redirect("admin_dashboard")

# ===========================
# ELECTION GUIDELINES
# ===========================

def election_guidelines(request):

    # Check if student is logged in
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("student_login")

    # Get student details
    student = get_object_or_404(Student, id=student_id)

    # If already voted, send back to home page
    if student.has_voted:
        messages.error(request, "You have already voted.")
        return redirect("home")

    # Continue to candidate page after clicking the button
    if request.method == "POST":
        return redirect("student_candidates")

    return render(request, "student/election_guidelines.html")

# ===========================
# STUDENT CANDIDATES
# ===========================

def student_candidates(request):

    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("student_login")

    student = get_object_or_404(Student, id=student_id)

    if student.has_voted:
        messages.error(request, "You have already voted.")
        return redirect("home")

    election = Election.objects.first()

    if not election or not election.is_active:
        messages.error(request, "Election is not active.")
        return redirect("home")

    positions = list(
        Candidate.objects.values_list(
            "position",
            flat=True
        ).distinct()
    )

    if not positions:
        messages.error(request, "No candidates available.")
        return redirect("home")

    step = int(request.GET.get("step", 0))

    if step >= len(positions):
        return redirect("confirm_vote")

    position = positions[step]

    candidates = Candidate.objects.filter(
        position=position
    )

    if request.method == "POST":

        selected_candidate = request.POST.get("candidate")

        if not selected_candidate:
            messages.error(
                request,
                "Please select one candidate."
            )
            return redirect(
                f"/student-candidates/?step={step}"
            )

        votes = request.session.get("votes", {})

        votes[position] = selected_candidate

        request.session["votes"] = votes

        return redirect(
            f"/student-candidates/?step={step+1}"
        )
    votes = request.session.get("votes", {})
    selected_candidate = votes.get(position)

    return render(
    request,
    "student/student_candidates.html",
    {
        "position": position,
        "candidates": candidates,
        "step": step,
        "last_step": len(positions) - 1,
        "selected_candidate": selected_candidate,
    }
)

# ===========================
# CONFIRM VOTE
# ===========================

def confirm_vote(request):

    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("student_login")

    votes = request.session.get("votes", {})

    selected_candidates = []

    for position, candidate_id in votes.items():

        candidate = Candidate.objects.get(
            id=candidate_id
        )

        selected_candidates.append({
            "position": position,
            "candidate": candidate
        })

    return render(
        request,
        "student/confirm_vote.html",
        {
            "selected_candidates": selected_candidates
        }
    )


# ===========================
# SUBMIT VOTE
# ===========================

def submit_vote(request):

    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("student_login")

    student = Student.objects.get(
        id=student_id
    )

    if student.has_voted:

        messages.error(
            request,
            "You have already voted."
        )

        return redirect("home")

    votes = request.session.get("votes", {})

    for position, candidate_id in votes.items():

        candidate = Candidate.objects.get(
            id=candidate_id
        )

        Vote.objects.create(
            student=student,
            candidate=candidate,
            position=position
        )

    student.has_voted = True
    student.save()

    request.session.pop("votes", None)

    messages.success(
        request,
        "Your vote has been submitted successfully."
    )

    return redirect("vote_success")

from django.db.models import Count

@login_required
def election_results(request):

    candidates = Candidate.objects.annotate(
    total_votes=Count("vote")
    )

    position_order = [
        "President",
        "Vice President",
        "Secretary",
        "Joint Secretary",
        "Treasurer",
        "Cultural",
        "Sports",
        "Placement",
        "Brand Ambassador",
    ]

    candidates = sorted(
     candidates,
        key=lambda c: (
            position_order.index(c.position),
            -c.total_votes
        )
    )

    # Position winners
    positions = Candidate.objects.values_list(
        "position",
        flat=True
    ).distinct()

    position_winners = {}

    for position in positions:

        position_candidates = Candidate.objects.filter(
            position=position
        ).annotate(
            total_votes=Count("vote")
        ).order_by("-total_votes")

        if position_candidates.exists():

            highest_votes = position_candidates.first().total_votes

            winners = position_candidates.filter(
                total_votes=highest_votes
            )

            position_winners[position] = winners

    votes_list = Vote.objects.select_related(
        "student",
        "candidate"
    )

    # ← PASTE STEP 3 HERE

    labels = []
    vote_data = []

    for c in candidates:
        labels.append(c.name)
        vote_data.append(c.total_votes)

    return render(
        request,
        "admin_panel/results.html",
        {
            "candidates": candidates,
            "position_winners": position_winners,
            "votes": votes_list,
            "labels": labels,
            "vote_data": vote_data,
        }
    )

from .models import Vote, Student

@login_required
def reset_election(request):
    # Delete all votes
    Vote.objects.all().delete()

    # Allow all students to vote again
    Student.objects.update(has_voted=False)

    # Clear election status (optional)
    election = Election.objects.first()
    if election:
        election.is_active = False
        election.save()

    messages.success(request, "Election has been reset successfully.")

    return redirect("admin_dashboard")

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse
from .models import Candidate

def export_results_pdf(request):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="election_results.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph("Election Results Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    candidates = Candidate.objects.all()

    data = [["Name", "Position", "Votes"]]

    for c in candidates:
        votes = c.vote_set.count()
        data.append([c.name, c.position, str(votes)])

    table = Table(data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))

    elements.append(table)

    doc.build(elements)

    return response

def vote_success(request):

    if "student_id" not in request.session:
        return redirect("student_login")

    return render(request, "student/vote_success.html")

def student_logout(request):

    request.session.flush()

    messages.success(request, "Logged out successfully.")

    return redirect("home")