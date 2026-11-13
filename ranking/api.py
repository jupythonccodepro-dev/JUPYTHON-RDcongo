from rest_framework.views import APIView
from rest_framework.response import Response
from .services import get_public_member_directory


class RankingAPIView(APIView):
    def get(self, request):
        return Response(get_public_member_directory(request.user))
