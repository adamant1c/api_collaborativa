from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer per la registrazione utente.
    """
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)

    # Campi personalizzati per nomi più intuitivi
    nome = serializers.CharField(source='first_name', required=True)
    cognome = serializers.CharField(source='last_name', required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm',
                  'nome', 'cognome']
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate(self, attrs):
        """Valida che le password coincidano"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Le password non coincidono'
            })
        return attrs

    def validate_email(self, value):
        """Verifica che l'email non sia già in uso"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Un utente con questa email esiste già'
            )
        return value

    def create(self, validated_data):
        """Crea l'utente con password hashata"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer per il profilo utente.
    """
    nome = serializers.CharField(source='first_name', required=False)
    cognome = serializers.CharField(source='last_name', required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nome', 'cognome',
                  'date_joined', 'last_login']
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']

    def validate_email(self, value):
        """Verifica che l'email non sia già in uso da altri"""
        user = self.instance
        if user and User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError(
                'Un utente con questa email esiste già'
            )
        return value