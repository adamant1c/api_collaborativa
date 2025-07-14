
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import UserRegistrationSerializer, UserProfileSerializer
import logging

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """
    Registrazione nuovo utente.
    """
    logging.info("Dati ricevuti:", request.data)  # Debug

    serializer = UserRegistrationSerializer(data=request.data)

    logging.info("Serializer valido:", serializer.is_valid())  # Debug
    logging.info("Errori serializer:", serializer.errors)  # Debug

    if serializer.is_valid():
        user = serializer.save()

        # Crea i token JWT
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'Utente registrato con successo',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'nome': user.first_name,
                'cognome': user.last_name,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

    # Restituisce gli errori dettagliati
    return Response({
        'errors': serializer.errors,
        'received_data': request.data
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    """
    Login utente con username/email e password.
    Restituisce token JWT.
    """
    username_or_email = request.data.get('username')
    password = request.data.get('password')

    if not username_or_email or not password:
        return Response({
            'error': 'Username/email e password sono richiesti'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Prova prima con username, poi con email
    user = authenticate(username=username_or_email, password=password)

    if not user:
        # Prova con email
        try:
            user_obj = User.objects.get(email=username_or_email)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass

    if user and user.is_active:
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'Login effettuato con successo',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'nome': user.first_name,
                'cognome': user.last_name,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)

    return Response({
        'error': 'Credenziali non valide'
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    """
    Logout utente - invalida il refresh token.
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        return Response({
            'message': 'Logout effettuato con successo'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': 'Errore durante il logout'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile(request):
    """
    Restituisce il profilo dell'utente corrente.
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)

