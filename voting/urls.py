from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('student-login/', views.student_login, name='student_login'),

    path('admin-login/', views.admin_login, name='admin_login'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path("results/",views.election_results,name="results"),

    path('import-students/', views.import_students_view, name='import_students'),
    path('add-candidate/', views.add_candidate, name='add_candidate'),
    path('candidates/', views.candidate_list, name='candidate_list'),

    path('start-election/', views.start_election, name='start_election'),
    path('end-election/', views.end_election, name='end_election'),

    path('delete-candidate/<int:id>/', views.delete_candidate, name='delete_candidate'),

    path("student-candidates/",views.student_candidates,name="student_candidates"),
    path("confirm-vote/",views.confirm_vote,name="confirm_vote"),
    path("submit-vote/",views.submit_vote,name="submit_vote"),
    path("reset-election/", views.reset_election, name="reset_election"),
    path("export-results-pdf/", views.export_results_pdf, name="export_results_pdf"),
    path("vote-success/",views.vote_success,name="vote_success"),
    path("student-logout/",views.student_logout,name="student_logout"),
    path("election-guidelines/",views.election_guidelines,name="election_guidelines"),

]