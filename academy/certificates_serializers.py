from rest_framework import serializers
from .models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    formation_title = serializers.CharField(source='formation.title', read_only=True)
    verification_scope = serializers.SerializerMethodField()

    @staticmethod
    def get_verification_scope(certificate):
        return (
            "Jupython se limite à examiner le justificatif que vous soumettez. "
            "Seul l'organisme ayant délivré le document peut confirmer son authenticité. "
            "Jupython ne délivre pas de certificats pour les parcours hébergés sur la plateforme."
        )

    class Meta:
        model = Certificate
        fields = [
            'id',
            'user',
            'formation',
            'formation_title',
            'certificate_url',
            'verified',
            'verification_scope',
            'issued_at',
            'verified_at',
        ]
        read_only_fields = ['verified', 'verified_at', 'issued_at']
