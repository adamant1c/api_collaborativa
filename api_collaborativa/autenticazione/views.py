
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, UserProfileSerializer
import logging




@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """
    Registra un nuovo utente nel sistema.

    ## Metodo
    POST

    ## Autenticazione
    Non richiesta

    ## Body JSON
    I campi richiesti dipendono dal `UserRegistrationSerializer`, ma generalmente includono:

    - **username**: *string* — Nome utente univoco
    - **email**: *string* — Indirizzo email valido
    - **password**: *string* — Password dell'utente
    - **nome**: *string* — Nome proprio (first name)
    - **cognome**: *string* — Cognome (last name)

    ## Esempio di richiesta
    ```json
    {
        "username": "mario",
        "email": "mario.rossi@example.com",
        "password": "password123",
        "nome": "Mario",
        "cognome": "Rossi"
    }
    ```

    ## Risposte
    - **201 Created**
        ```json
        {
            "message": "Utente registrato con successo",
            "user": {
                "id": 1,
                "username": "mario",
                "email": "mario.rossi@example.com",
                "nome": "Mario",
                "cognome": "Rossi"
            },
            "tokens": {
                "refresh": "jwt_refresh_token",
                "access": "jwt_access_token"
            }
        }
        ```

    - **400 Bad Request**
        ```json
        {
            "errors": {
                "email": ["Questo campo è obbligatorio."]
            },
            "received_data": {
                "username": "mario",
                "email": "",
                "password": "password123",
                "nome": "Mario",
                "cognome": "Rossi"
            }
        }
        ```

    ## Note
    Dopo la registrazione, l'utente riceve automaticamente una coppia di token JWT (refresh e access).
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
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    """
       Effettua il logout dell'utente autenticato invalidando il token di refresh.

       ## Metodo
       POST

       ## Autenticazione
       Richiesta (token JWT nel header Authorization)

       ## Body JSON
       - **refresh**: *string* — Token di refresh JWT da invalidare

       ## Esempio di richiesta
       ```json
       {
           "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
       }
       ```

       ## Risposte
       - **200 OK**
           - `{"message": "Logout effettuato con successo"}`
       - **400 Bad Request**
           - `{"error": "Errore durante il logout; ..."}`
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
        logging.error(f'error: {e}')
        return Response({
            'error': f'Errore durante il logout; {e}'
        }, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile(request):
    """
    Restituisce il profilo dell'utente autenticato.

    ## Metodo
    GET

    ## Autenticazione
    Richiesta (token JWT nel header Authorization)

    ## Parametri
    Nessuno

    ## Risposte
    - **200 OK**
        ```json
        {
            "id": 1,
            "username": "utente1",
            "email": "utente@example.com",
            "nome": "Mario",
            "cognome": "Rossi"
        }
        ```

    ## Note
    I campi restituiti dipendono da `UserProfileSerializer`.
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)

