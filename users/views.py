from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .services.registration import register_company, register_assessor, generate_one_time_code, register_assessee
from .models import CompanySerializer, AssessorSerializer, CompanyOneTimeLinkCodeSerializer, AssesseeSerializer
import json


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_assessor_one_time_code(request):
    company_email = request.user.email
    one_time_code = generate_one_time_code(company_email)
    response_data = CompanyOneTimeLinkCodeSerializer(one_time_code).data
    return Response(data=response_data)


@api_view(['POST'])
def serve_register_company(request):
    """
    request_data must contain
    email,
    password,
    confirmed_password,
    company_name,
    company_description,
    company_address
    """
    request_data = json.loads(request.body.decode('utf-8'))
    company = register_company(request_data)
    response_data = CompanySerializer(company).data
    return Response(data=response_data)


@api_view(['POST'])
def serve_register_assessor(request):
    """
        request_data must contain
        email,
        password,
        confirmed_password,
        first_name,
        last_name,
        phone_number,
        employee_id,
        one_time_code
    """
    request_data = json.loads(request.body.decode('utf-8'))
    assessor = register_assessor(request_data)
    response_data = AssessorSerializer(assessor).data
    return Response(data=response_data)


@api_view(['POST'])
def serve_register_assessee(request):
    """
        request_data must contain
        email,
        password,
        confirmed_password,
        first_name,
        last_name,
        phone_number,
        date_of_birth,
    """
    request_data = json.loads(request.body.decode('utf-8'))
    assessee = register_assessee(request_data)
    response_data = AssesseeSerializer(assessee).data
    return Response(data=response_data)
