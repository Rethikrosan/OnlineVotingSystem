from django.contrib import admin
from .models import Student, Candidate, Vote, Election


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("roll_number", "name", "has_voted")


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("name", "position")


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("student", "candidate", "position", "voted_at")


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ("is_active",)