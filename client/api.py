from django.http import HttpRequest
from django.shortcuts import render
from ninja import Router

from client.models import ContractType
from client.schemas import ContractTypeSchema
from system.schemas import EmptyResponseSchema

router = Router()


@router.get("/contract-types", response=list[ContractTypeSchema])
def contract_types(request: HttpRequest):
    return ContractType.objects.all()


@router.post("/contract-types/add", response={201: ContractTypeSchema})
def add_contract_type(request: HttpRequest, content_type: ContractTypeSchema):
    type = ContractType.objects.create(name=content_type.name)
    if type.id:
        return 201, ContractTypeSchema.from_orm(type)


@router.delete("/contract-types/{int:id}/delete", response={204: EmptyResponseSchema})
def delete_contract_type(request: HttpRequest, id: int):
    ContractType.objects.filter(id=id).delete()
    return 204, {}
