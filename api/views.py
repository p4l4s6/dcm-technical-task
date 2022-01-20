import random

from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import TestRunRequest, TestFilePath
from api.serializers import TestRunRequestSerializer, TestRunRequestItemSerializer, TestCaseUploadSerializer
from api.tasks import execute_test_run_request
from api.usecases import get_assets


class TestRunRequestAPIView(ListCreateAPIView):
    serializer_class = TestRunRequestSerializer
    queryset = TestRunRequest.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        instance = serializer.save()
        execute_test_run_request.delay(instance.id)


class TestRunRequestItemAPIView(RetrieveAPIView):
    serializer_class = TestRunRequestItemSerializer
    queryset = TestRunRequest.objects.all()
    lookup_field = 'pk'


class AssetsAPIView(APIView):

    def get(self, request):
        return Response(status=status.HTTP_200_OK, data=get_assets())


class UploadTestCase(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request):
        serializer = TestCaseUploadSerializer(data=request.data)
        if serializer.is_valid():
            test_file = serializer.validated_data['test_file']
            file_path = f"sample-tests/test_{test_file.name}_{random.randint(1000, 9999)}.py"
            destination = open(file_path, 'wb+')
            for chunk in test_file.chunks():
                destination.write(chunk)
            destination.close()
            test_file_path = TestFilePath.objects.create(
                path=file_path
            )
            test_file_path.save()
            return Response({
                "id": test_file_path.id,
                "path": test_file_path.path
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
