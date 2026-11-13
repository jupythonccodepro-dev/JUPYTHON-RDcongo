from rest_framework import serializers
from .models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    formation_title = serializers.CharField(source='formation.title', read_only=True)
    verification_scope = serializers.SerializerMethodField()
    certificate_file_available = serializers.SerializerMethodField()

    @staticmethod
    def get_certificate_file_available(certificate):
        return bool(certificate.certificate_file)

    @staticmethod
    def get_verification_scope(certificate):
        return (
            "Jupython se limite \u00e0 examiner le justificatif que vous soumettez ; "
            "seul l\u2019organisme \u00e9metteur peut confirmer l\u2019authenticit\u00e9 du certificat. "
            "Jupython ne d\u00e9livre pas de certificats pour les parcours h\u00e9berg\u00e9s sur la plateforme."
        )

    class Meta:
        model = Certificate
        fields = [
            'id',
            'user',
            'formation',
            'formation_title',
            'certificate_url',
            'certificate_file_available',
            'verified',
            'verification_scope',
            'issued_at',
            'verified_at',
        ]
        read_only_fields = ['verified', 'verified_at', 'issued_at']
