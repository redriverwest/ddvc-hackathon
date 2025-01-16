from domain.models import Company


def generate_companies():
    yield Company(
        name="startupradar",
        description="very great company",
        domain="startupradar.co",
        linkedin_url="https://linkedin.com/company/startupradar",
        industry="data analysis",
        location="Berlin, Germany",
        primary_contact=None,
    )
