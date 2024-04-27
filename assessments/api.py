from ninja import Router

from assessments.models import Assessment, AssessmentDomain
from assessments.schemas import (
    AssessmentDomainInput,
    AssessmentDomainSchema,
    AssessmentLevelSchema,
)
from system.schemas import EmptyResponseSchema

router = Router()


@router.get("/domains", response=list[AssessmentDomainSchema])
def assessments(request):
    return AssessmentDomain.objects.all()


@router.post("/domains/add", response={201: AssessmentDomainSchema})
def add_assessment_domain(request, assessment_domain: AssessmentDomainInput):
    # Create the domain first
    domain = AssessmentDomain.objects.create(name=assessment_domain.name)

    # Create the assessment
    for assessment_level in assessment_domain.levels:
        Assessment.objects.create(
            level=assessment_level.level, domain=domain, content=assessment_level.assessments
        )

    return 201, domain


@router.delete("/domains/{int:id}/delete", response={204: EmptyResponseSchema})
def delete_assessment_domain(request, id: int):
    # delete a domain
    try:
        AssessmentDomain.objects.filter(id=id).delete()
        return 201
    except Exception:
        pass
