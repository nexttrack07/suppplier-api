from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Test cases for Tags api"""

    def setUp(self):
        self.client = APIClient()

    def test_tag_get_without_auth(self):
        """Test that tags GET returns 401"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test cases for private tags api"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='tes@gmail.com', password='testpass')
        self.client = APIClient()

        self.client.force_authenticate(user=self.user)

    def test_retreive_tags(self):
        """Test that an authenticated user can retrieve their tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """test that tags are limited to each user that creates them"""
        new_user = get_user_model().objects.create_user(
            'test2@gm.com',
            'password22'
        )
        Tag.objects.create(user=new_user, name='Fruity')

        tag = Tag.objects.create(user=self.user, name='Meaty')
        res = self.client.get(TAGS_URL)  # request for the self.user user

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

        self.assertEqual(res.data[0]['name'], tag.name)
