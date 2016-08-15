from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import serializers, viewsets, status


class UserSerializer(serializers.HyperlinkedModelSerializer):
    queryset = User.objects.all()

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @list_route(methods=['post'])
    def bind(self, request, *args, **kwargs):
        user = authenticate(
            username=request.data['username'],
            password=request.data['password'], )
        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return Response(status=status.HTTP_204_NO_CONTENT)
