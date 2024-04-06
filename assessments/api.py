from ninja import Router

from assessments.models import Assessment, AssessmentDomain
from assessments.schemas import AssessmentDomainSchema, AssessmentLevelSchema
from system.schemas import EmptyResponseSchema

router = Router()


@router.get("/matrix", response=list[AssessmentDomainSchema])
def assessments(request):
    domains = AssessmentDomain.objects.all()

    results: list[AssessmentDomainSchema] = []

    for domain in domains:
        levels = [
            AssessmentLevelSchema(level=assessment.level, assessments=str(assessment.content))
            for assessment in domain.assessments.all()
        ]
        results.append(AssessmentDomainSchema(name=domain.name, levels=levels))

    return results


@router.post("/domain/add", response={201: EmptyResponseSchema})
def add_assessment_domain(request, assessment_domain: AssessmentDomainSchema):
    # Create the domain first
    domain = AssessmentDomain.objects.create(name=assessment_domain.name)

    # Create the assessment
    for level in assessment_domain.levels:
        Assessment.objects.create(level=level, domain=domain, content=assessment_domain.content)

    return 201


@router.delete("/domain/{int:id}/delete", response={204: EmptyResponseSchema})
def delete_assessment_domain(request, id: int):
    # delete a domain
    try:
        AssessmentDomain.objects.filter(id=id).delete()
        return 201
    except Exception:
        pass
