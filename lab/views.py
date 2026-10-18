from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from .models import Topic, SubTopic, Section
from .forms import SectionForm, TopicForm, SubTopicForm


def staff_required(view):
    return user_passes_test(
        lambda u: u.is_authenticated and u.is_staff, login_url="/admin/login/"
    )(view)


def _sidebar_topics():
    """Topics → subtopics (with section counts) for the sidebar tree."""
    return (
        Topic.objects.prefetch_related("subtopics")
        .annotate(subtopic_count=Count("subtopics", distinct=True))
        .all()
    )


# ───────────────────────────── Public views ─────────────────────────────


def home(request):
    topics = Topic.objects.annotate(
        subtopic_count=Count("subtopics", distinct=True),
        section_count=Count("subtopics__sections", distinct=True),
    )
    return render(
        request,
        "lab/home.html",
        {
            "topics": _sidebar_topics(),
            "home_topics": topics,
        },
    )


def topic_detail(request, slug):
    """Topic page — lists all its subtopics as cards."""
    topic = get_object_or_404(Topic, slug=slug)
    subtopics = topic.subtopics.annotate(section_count=Count("sections"))
    return render(
        request,
        "lab/topic_detail.html",
        {
            "topics": _sidebar_topics(),
            "topic": topic,
            "subtopics": subtopics,
        },
    )


def subtopic_detail(request, topic_slug, subtopic_slug):
    """SubTopic page — single page showing all its sections."""
    topic = get_object_or_404(Topic, slug=topic_slug)
    subtopic = get_object_or_404(SubTopic, topic=topic, slug=subtopic_slug)
    sections = subtopic.sections.all()
    return render(
        request,
        "lab/subtopic_detail.html",
        {
            "topics": _sidebar_topics(),
            "topic": topic,
            "subtopic": subtopic,
            "sections": sections,
        },
    )


def search(request):
    query = request.GET.get("q", "").strip()
    results = []
    if query:
        results = (
            Section.objects.select_related("subtopic__topic")
            .filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(code__icontains=query)
                | Q(output__icontains=query)
                | Q(subtopic__name__icontains=query)
                | Q(subtopic__topic__name__icontains=query)
                | Q(language__icontains=query)
            )
            .order_by("subtopic__topic__order", "subtopic__order", "order")
        )

    # Also match subtopic names directly
    subtopic_results = []
    if query:
        subtopic_results = (
            SubTopic.objects.select_related("topic")
            .filter(Q(name__icontains=query) | Q(description__icontains=query))
            .order_by("topic__order", "order")
        )

    return render(
        request,
        "lab/search.html",
        {
            "topics": _sidebar_topics(),
            "query": query,
            "results": results,
            "subtopic_results": subtopic_results,
            "count": len(results) + len(subtopic_results) if query else 0,
        },
    )


# ───────────────────────────── Section editing (public / logged-in) ─────────────────────────────


@login_required
def section_add(request, topic_slug, subtopic_slug):
    subtopic = get_object_or_404(SubTopic, topic__slug=topic_slug, slug=subtopic_slug)
    if request.method == "POST":
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.subtopic = subtopic
            section.save()
            messages.success(request, "Section added successfully.")
            return redirect(subtopic.get_absolute_url())
    else:
        form = SectionForm()
    return render(
        request,
        "lab/section_form.html",
        {
            "form": form,
            "subtopic": subtopic,
            "topic": subtopic.topic,
            "topics": _sidebar_topics(),
        },
    )


@login_required
def section_edit(request, pk):
    section = get_object_or_404(Section, pk=pk)
    if request.method == "POST":
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, "Section updated.")
            return redirect(section.subtopic.get_absolute_url())
    else:
        form = SectionForm(instance=section)
    return render(
        request,
        "lab/section_form.html",
        {
            "form": form,
            "subtopic": section.subtopic,
            "topic": section.subtopic.topic,
            "topics": _sidebar_topics(),
        },
    )


@login_required
def section_delete(request, pk):
    section = get_object_or_404(Section, pk=pk)
    subtopic = section.subtopic
    if request.method == "POST":
        section.delete()
        messages.success(request, "Section deleted.")
        return redirect(subtopic.get_absolute_url())
    return render(
        request,
        "lab/section_confirm_delete.html",
        {
            "section": section,
            "subtopic": subtopic,
            "topic": subtopic.topic,
            "topics": _sidebar_topics(),
        },
    )


# ───────────────────────────── Custom Admin Dashboard ─────────────────────────────


@staff_required
def dashboard(request):
    topics = Topic.objects.annotate(
        subtopic_count=Count("subtopics", distinct=True),
        section_count=Count("subtopics__sections", distinct=True),
    )
    stats = {
        "topics": topics.count(),
        "subtopics": SubTopic.objects.count(),
        "sections": Section.objects.count(),
        "recent": Section.objects.count(),  # placeholder
    }
    recent_sections = Section.objects.select_related("subtopic__topic").order_by(
        "-updated_at"
    )[:6]

    return render(
        request,
        "lab/dashboard.html",
        {
            "topics": topics,
            "stats": stats,
            "recent_sections": recent_sections,
        },
    )


@staff_required
def dashboard_topic_add(request):
    if request.method == "POST":
        form = TopicForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Topic created.")
            return redirect("lab:dashboard")
    else:
        form = TopicForm()
    return render(
        request, "lab/dashboard_topic_form.html", {"form": form, "mode": "add"}
    )


@staff_required
def dashboard_topic_edit(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    if request.method == "POST":
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            form.save()
            messages.success(request, "Topic updated.")
            return redirect("lab:dashboard")
    else:
        form = TopicForm(instance=topic)
    return render(
        request,
        "lab/dashboard_topic_form.html",
        {"form": form, "mode": "edit", "topic": topic},
    )


@staff_required
def dashboard_topic_delete(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    if request.method == "POST":
        topic.delete()
        messages.success(request, "Topic deleted.")
        return redirect("lab:dashboard")
    return render(
        request, "lab/dashboard_confirm_delete.html", {"topic": topic, "kind": "topic"}
    )


@staff_required
def dashboard_topic_subtopics(request, slug):
    """List subtopics in a topic (dashboard)."""
    topic = get_object_or_404(Topic, slug=slug)
    subtopics = topic.subtopics.annotate(section_count=Count("sections"))
    return render(
        request,
        "lab/dashboard_topic.html",
        {
            "topic": topic,
            "subtopics": subtopics,
        },
    )


@staff_required
def dashboard_subtopic_add(request, topic_slug):
    topic = get_object_or_404(Topic, slug=topic_slug)
    if request.method == "POST":
        form = SubTopicForm(request.POST)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.topic = topic
            sub.save()
            messages.success(request, "SubTopic created.")
            return redirect("lab:dashboard_topic_subtopics", slug=topic.slug)
    else:
        form = SubTopicForm()
    return render(
        request,
        "lab/dashboard_subtopic_form.html",
        {
            "form": form,
            "mode": "add",
            "topic": topic,
        },
    )


@staff_required
def dashboard_subtopic_edit(request, pk):
    subtopic = get_object_or_404(SubTopic, pk=pk)
    if request.method == "POST":
        form = SubTopicForm(request.POST, instance=subtopic)
        if form.is_valid():
            form.save()
            messages.success(request, "SubTopic updated.")
            return redirect("lab:dashboard_topic_subtopics", slug=subtopic.topic.slug)
    else:
        form = SubTopicForm(instance=subtopic)
    return render(
        request,
        "lab/dashboard_subtopic_form.html",
        {
            "form": form,
            "mode": "edit",
            "topic": subtopic.topic,
            "subtopic": subtopic,
        },
    )


@staff_required
def dashboard_subtopic_delete(request, pk):
    subtopic = get_object_or_404(SubTopic, pk=pk)
    if request.method == "POST":
        topic_slug = subtopic.topic.slug
        subtopic.delete()
        messages.success(request, "SubTopic deleted.")
        return redirect("lab:dashboard_topic_subtopics", slug=topic_slug)
    return render(
        request,
        "lab/dashboard_confirm_delete.html",
        {
            "subtopic": subtopic,
            "topic": subtopic.topic,
            "kind": "subtopic",
        },
    )


@staff_required
def dashboard_subtopic_sections(request, pk):
    """Manage sections inside a subtopic (dashboard)."""
    subtopic = get_object_or_404(SubTopic.objects.select_related("topic"), pk=pk)
    sections = subtopic.sections.all()
    return render(
        request,
        "lab/dashboard_subtopic.html",
        {
            "subtopic": subtopic,
            "topic": subtopic.topic,
            "sections": sections,
        },
    )


@staff_required
def dashboard_section_add(request, subtopic_pk):
    subtopic = get_object_or_404(
        SubTopic.objects.select_related("topic"), pk=subtopic_pk
    )
    if request.method == "POST":
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.subtopic = subtopic
            section.save()
            messages.success(request, "Section added.")
            return redirect("lab:dashboard_subtopic_sections", pk=subtopic.pk)
    else:
        form = SectionForm()
    return render(
        request,
        "lab/dashboard_section_form.html",
        {
            "form": form,
            "subtopic": subtopic,
            "topic": subtopic.topic,
            "mode": "add",
        },
    )


@staff_required
def dashboard_section_edit(request, pk):
    section = get_object_or_404(
        Section.objects.select_related("subtopic__topic"), pk=pk
    )
    if request.method == "POST":
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, "Section updated.")
            return redirect("lab:dashboard_subtopic_sections", pk=section.subtopic.pk)
    else:
        form = SectionForm(instance=section)
    return render(
        request,
        "lab/dashboard_section_form.html",
        {
            "form": form,
            "subtopic": section.subtopic,
            "topic": section.subtopic.topic,
            "mode": "edit",
            "section": section,
        },
    )


@staff_required
def dashboard_section_delete(request, pk):
    section = get_object_or_404(
        Section.objects.select_related("subtopic__topic"), pk=pk
    )
    subtopic = section.subtopic
    if request.method == "POST":
        section.delete()
        messages.success(request, "Section deleted.")
        return redirect("lab:dashboard_subtopic_sections", pk=subtopic.pk)
    return render(
        request,
        "lab/dashboard_confirm_delete.html",
        {
            "section": section,
            "subtopic": subtopic,
            "topic": subtopic.topic,
            "kind": "section",
        },
    )
