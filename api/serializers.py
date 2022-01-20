from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from api.models import TestRunRequest, TestFilePath, TestEnvironment


class TestRunRequestSerializer(serializers.ModelSerializer):
    env_name = serializers.ReadOnlyField(source='env.name')

    class Meta:
        model = TestRunRequest
        fields = (
            'id',
            'requested_by',
            'env',
            'path',
            'status',
            'created_at',
            'env_name'
        )
        read_only_fields = (
            'id',
            'created_at',
            'status',
            'logs',
            'env_name'
        )


class TestRunRequestItemSerializer(serializers.ModelSerializer):
    env_name = serializers.ReadOnlyField(source='env.name')

    class Meta:
        model = TestRunRequest
        fields = (
            'id',
            'requested_by',
            'env',
            'path',
            'status',
            'created_at',
            'env_name',
            'logs'
        )


class TestFilePathSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestFilePath
        fields = ('id', 'path')


class TestEnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestEnvironment
        fields = ('id', 'name')

class TestCaseUploadSerializer(serializers.Serializer):
    test_file=serializers.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['py'])]
    )