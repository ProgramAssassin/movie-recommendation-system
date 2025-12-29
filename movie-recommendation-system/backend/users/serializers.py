from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, UserRating, UserWatchlist
from movies.serializers import MovieListSerializer


class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "两次密码不一致"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("用户名或密码错误")
            if not user.is_active:
                raise serializers.ValidationError("用户账户已被禁用")
        else:
            raise serializers.ValidationError("必须提供用户名和密码")
        
        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""
    ratings_count = serializers.SerializerMethodField()
    watchlist_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'avatar', 'bio', 'birth_date', 'date_joined', 'last_login',
                 'ratings_count', 'watchlist_count']
        read_only_fields = ['date_joined', 'last_login']
    
    def get_ratings_count(self, obj):
        return obj.ratings.count()
    
    def get_watchlist_count(self, obj):
        return obj.watchlist.count()


class UserRatingSerializer(serializers.ModelSerializer):
    """用户评分序列化器"""
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = UserRating
        fields = ['id', 'user', 'movie', 'movie_id', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        validated_data.pop('movie_id', None)
        return super().update(instance, validated_data)


class UserWatchlistSerializer(serializers.ModelSerializer):
    """用户观看列表序列化器"""
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = UserWatchlist
        fields = ['id', 'user', 'movie', 'movie_id', 'added_at']
        read_only_fields = ['user', 'added_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserPreferenceSerializer(serializers.ModelSerializer):
    """用户偏好序列化器"""
    preferred_genres = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CustomUser._meta.get_field('preferred_genres').related_model.objects.all()
    )
    
    class Meta:
        model = CustomUser
        fields = ['preferred_genres']