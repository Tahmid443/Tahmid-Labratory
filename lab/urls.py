from django.urls import path
from . import views

app_name = "lab"

urlpatterns = [
    # Public
    path("", views.home, name="home"),
    path("search/", views.search, name="search"),
    path("topic/<slug:slug>/", views.topic_detail, name="topic_detail"),
    path(
        "topic/<slug:topic_slug>/<slug:subtopic_slug>/",
        views.subtopic_detail,
        name="subtopic_detail",
    ),
    # Public section editing
    path(
        "topic/<slug:topic_slug>/<slug:subtopic_slug>/section/add/",
        views.section_add,
        name="section_add",
    ),
    path("section/<int:pk>/edit/", views.section_edit, name="section_edit"),
    path("section/<int:pk>/delete/", views.section_delete, name="section_delete"),
    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/topic/add/", views.dashboard_topic_add, name="dashboard_topic_add"),
    path(
        "dashboard/topic/<int:pk>/edit/",
        views.dashboard_topic_edit,
        name="dashboard_topic_edit",
    ),
    path(
        "dashboard/topic/<int:pk>/delete/",
        views.dashboard_topic_delete,
        name="dashboard_topic_delete",
    ),
    path(
        "dashboard/topic/<slug:slug>/",
        views.dashboard_topic_subtopics,
        name="dashboard_topic_subtopics",
    ),
    path(
        "dashboard/topic/<slug:topic_slug>/subtopic/add/",
        views.dashboard_subtopic_add,
        name="dashboard_subtopic_add",
    ),
    path(
        "dashboard/subtopic/<int:pk>/edit/",
        views.dashboard_subtopic_edit,
        name="dashboard_subtopic_edit",
    ),
    path(
        "dashboard/subtopic/<int:pk>/delete/",
        views.dashboard_subtopic_delete,
        name="dashboard_subtopic_delete",
    ),
    path(
        "dashboard/subtopic/<int:pk>/",
        views.dashboard_subtopic_sections,
        name="dashboard_subtopic_sections",
    ),
    path(
        "dashboard/subtopic/<int:subtopic_pk>/section/add/",
        views.dashboard_section_add,
        name="dashboard_section_add",
    ),
    path(
        "dashboard/section/<int:pk>/edit/",
        views.dashboard_section_edit,
        name="dashboard_section_edit",
    ),
    path(
        "dashboard/section/<int:pk>/delete/",
        views.dashboard_section_delete,
        name="dashboard_section_delete",
    ),
]
