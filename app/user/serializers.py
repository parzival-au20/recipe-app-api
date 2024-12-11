"""
Serializers for the user API View
"""
from django.contrib.auth import authenticate

from django.utils.translation import gettext as _
from core.models import User, Address, Company, Geo

from rest_framework import serializers


class GeoSerializer(serializers.ModelSerializer):
    lat = serializers.DecimalField(max_digits=12, decimal_places=9)
    lng = serializers.DecimalField(max_digits=12, decimal_places=9)

    class Meta:
        model = Geo
        fields = ['lat', 'lng']


class AddressSerializer(serializers.ModelSerializer):
    geo = GeoSerializer()

    class Meta:
        model = Address
        fields = ['street', 'suite', 'city', 'zipcode', 'geo']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['name']


class UserSerializer(serializers.ModelSerializer):
    """ Serializer for the user object."""

    address = AddressSerializer(required=False, allow_null=True)  # Address alanını include et
    company = CompanySerializer(required=False, allow_null=True)  # Company alanını include et

    class Meta:
        model = User
        fields = ['email', 'password', 'name', 'username', 'address', 'phone', 'website', 'company']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        address_data = validated_data.pop('address', None)
        company_data = validated_data.pop('company', None)
        password = validated_data.pop('password', None)

        # Kullanıcıyı oluştur
        user = User.objects.create_user(**validated_data)

        # Address ve Company verilerini işle
        if address_data:
            self._handle_address_creation(user, address_data)
        if company_data:
            self._handle_company_creation(user, company_data)

        if password:
            user.set_password(password)
            user.save()

        return user

    def update(self, instance, validated_data):
        """Update and return user."""
        address_data = validated_data.pop('address', None)
        company_data = validated_data.pop('company', None)
        password = validated_data.pop('password', None)

        # Kullanıcıyı güncelle
        user = super().update(instance, validated_data)

        # Address ve Company verilerini güncelle
        if address_data:
            self._handle_address_update(user, address_data)
        if company_data:
            self._handle_company_update(user, company_data)

        if password:
            user.set_password(password)
            user.save()

        return user

    def _handle_address_creation(self, user, address_data):
        """Handle the creation of an address and associate with user."""
        geo_data = address_data.pop('geo', None)
        geo_instance = None
        if geo_data:
            geo_instance = Geo.objects.create(**geo_data)
        address = Address.objects.create(**address_data, geo=geo_instance)
        user.address = address
        user.save()

    def _handle_company_creation(self, user, company_data):
        """Handle the creation of a company and associate with user."""
        company = Company.objects.create(**company_data)
        user.company = company
        user.save()

    def _handle_address_update(self, user, address_data):
        """Handle updating the address data for the user."""
        geo_data = address_data.pop('geo', None)
        geo_instance = user.address.geo
        if geo_data:
            for attr, value in geo_data.items():
                setattr(geo_instance, attr, value)
            geo_instance.save()
        for attr, value in address_data.items():
            setattr(user.address, attr, value)
        user.address.save()

    def _handle_company_update(self, user, company_data):
        """Handle updating the company data for the user."""
        for attr, value in company_data.items():
            setattr(user.company, attr, value)
        user.company.save()


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password,
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
