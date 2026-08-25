from django.db.utils import OperationalError, ProgrammingError
from django.db.models.signals import post_migrate
from django.dispatch import receiver


CREW_ROLES = [
    ('tour-guide', 'Tour Guide'),
    ('translator', 'Translator'),
    ('local-host', 'Local Host'),
    ('local-fixer', 'Local Fixer'),
    ('driver', 'Independent Driver'),
    ('security-guard', 'Security Guard'),
    ('photographer', 'Photographer / Videographer'),
    ('medical-support', 'Medical Support'),
    ('logistics-assistant', 'Logistics Assistant'),
    ('cook', 'Cook / Camp Support'),
    ('porter', 'Porter'),
    ('cultural-expert', 'Cultural Expert'),
    ('mountain-guide', 'Mountain Guide'),
]

SUPPLIER_CATEGORIES = [
    ('hotel', 'Hotel'), ('guesthouse', 'Guesthouse / Homestay'),
    ('transport', 'Transport Company'), ('vehicle-rental', 'Vehicle Owner / Rental'),
    ('restaurant', 'Restaurant'), ('catering', 'Catering'),
    ('security-company', 'Security Company'), ('equipment', 'Equipment Rental'),
    ('tickets', 'Tickets and Activities'), ('permits', 'Permits and Documentation'),
    ('medical', 'Medical Services'), ('telecom', 'Telecom and SIM Services'),
    ('gifts', 'Gifts and Welcome Items'),
]


@receiver(post_migrate)
def seed_resource_reference_data(sender, **kwargs):
    if sender.name != 'tour':
        return
    from .models import CrewRole, SupplierCategory, TrainingCourse
    try:
        roles = {}
        for code, name in CREW_ROLES:
            role, _ = CrewRole.objects.get_or_create(code=code, defaults={'name': name})
            roles[code] = role
        for code, name in SUPPLIER_CATEGORIES:
            SupplierCategory.objects.get_or_create(code=code, defaults={'name': name})
        onboarding, _ = TrainingCourse.objects.get_or_create(
            code='afghanawaits-onboarding',
            defaults={
                'title': 'AfghanAwaits Workforce Onboarding',
                'description': 'Code of conduct, tour workflow, guest care, privacy and reporting.',
                'content': 'Complete the operational onboarding and acknowledge the code of conduct.',
                'passing_score': 80,
            },
        )
        onboarding.required_for_roles.set(roles.values())
        safety, _ = TrainingCourse.objects.get_or_create(
            code='tour-safety-basics',
            defaults={
                'title': 'Tour Safety and Incident Reporting',
                'description': 'Safety briefings, emergency communication and incident escalation.',
                'content': 'Learn the safety chain, emergency contacts and incident reporting standard.',
                'passing_score': 80,
            },
        )
        safety.required_for_roles.set(roles.values())
    except (OperationalError, ProgrammingError):
        # The legacy project creates local app tables with migrate --run-syncdb.
        # During first startup the tables may not exist yet.
        return
