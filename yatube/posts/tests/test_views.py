from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django import forms

from ..models import Group, Post, Follow

OBJECTS_TWO_PAGES = settings.ENTRIES_THE_PAGE // 2
TEST_OF_POST = settings.ENTRIES_THE_PAGE + OBJECTS_TWO_PAGES

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="Kirill")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.group2 = Group.objects.create(
            title="Тест группа",
            slug="testing-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
        )
        cls.templates_pages_names = [
            (reverse("posts:index"), "posts/index.html"),
            (reverse(
                "posts:group_list", kwargs={"slug": cls.group.slug}
            ), "posts/group_list.html"),
            (reverse(
                "posts:profile", kwargs={"username": cls.post.author}
            ), "posts/profile.html"),
            (reverse(
                "posts:post_detail", kwargs={"post_id": cls.post.id}
            ), "posts/post_detail.html"),
            (reverse(
                "posts:post_edit", kwargs={"post_id": cls.post.id}
            ), "posts/create_post.html"),
            (reverse("posts:post_create"), "posts/create_post.html"),
        ]
        cls.form_fields = [
            (("text"), (forms.fields.CharField)),
            (("group"), (forms.fields.ChoiceField)),
            (("image"), (forms.fields.ImageField)),
        ]

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in self.templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(template)
                self.assertTemplateUsed(response, reverse_name)

    def test_index_show_correct_context(self):
        """Список постов в шаблоне index равен ожидаемому контексту."""
        response = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(response.context.get("page_obj")[0], self.post)

    def test_group_list_show_correct_context(self):
        """Список постов в шаблоне group_list равен ожидаемому контексту."""
        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug})
        )
        self.assertEqual(response.context.get("page_obj")[0], self.post)
        self.assertEqual(response.context.get("group"), self.post.group)

    def test_profile_show_correct_context(self):
        """Список постов в шаблоне profile равен ожидаемому контексту."""
        response = self.authorized_client.get(
            reverse("posts:profile", args=(self.post.author,))
        )
        self.assertEqual(response.context.get("page_obj")[0], self.post)
        self.assertEqual(response.context.get("author"), self.post.author)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )
        self.assertEqual(response.context.get("post").text, self.post.text)
        self.assertEqual(response.context.get("post").author, self.post.author)
        self.assertEqual(response.context.get("post").group, self.post.group)

    def test_create_edit_show_correct_context(self):
        """Шаблон create_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id})
        )
        form_fields = self.form_fields
        for value, expected in form_fields:
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = self.form_fields
        for value, expected in form_fields:
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_check_group_in_pages(self):
        """Проверяем создание поста на страницах с выбранной группой"""
        form_fields = [
            (reverse("posts:index"), self.post),
            (reverse(
                "posts:group_list", kwargs={"slug": self.group.slug}
            ), self.post),
            (reverse(
                "posts:profile", kwargs={"username": self.post.author}
            ), self.post),
        ]
        for value, expected in form_fields:
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context["page_obj"]
                self.assertIn(expected, form_field)

    def test_check_group_not_in_mistake_group_list_page(self):
        """Проверяем чтобы созданный Пост с группой не попап в чужую группу."""
        res_1 = self.authorized_client.get(reverse('posts:group_list',
                                           kwargs={'slug': self.group2.slug}))
        context = res_1.context["page_obj"]
        self.assertNotIn(self.post, context)

    def test_nonexist_page_uses_correct_template(self):
        """Страница 404 отдаёт кастомный шаблон."""
        response = self.client.get('/nonexist-page/')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_image_in_index_and_profile_page(self):
        """Картинка передается на страницу index_group_list_and_profile."""
        templates = (
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": self.group.slug}),
            reverse("posts:profile", kwargs={"username": self.post.author}),
        )
        for url in templates:
            with self.subTest(url):
                response = self.authorized_client.get(url)
                context = response.context["page_obj"][0]
                self.assertEqual(context.image, self.post.image)

    def test_image_in_post_detail_page(self):
        """Картинка передается на страницу post_detail."""
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )
        context = response.context["post"]
        self.assertEqual(context.image, self.post.image)

    def test_check_cache(self):
        """Проверка кеша."""
        response = self.authorized_client.get(reverse("posts:index"))
        r_1 = response.content
        Post.objects.get(id=self.post.id).delete()
        response2 = self.authorized_client.get(reverse("posts:index"))
        r_2 = response2.content
        cache.clear()
        response3 = self.authorized_client.get(reverse("posts:index"))
        r_3 = response3.content
        self.assertEqual(r_1, r_2)
        self.assertNotEqual(r_2, r_3)

    def test_follow_author_post(self):
        """Проверка подписки на автора поста."""
        following_user = User.objects.create(username="following")
        self.authorized_client.get(reverse("posts:profile_follow",
                                           kwargs={'username':
                                                   following_user}))
        self.assertTrue(Follow.objects.filter(user=self.user,
                                              author=following_user).exists())

    def test_unfollow_author_post(self):
        """Проверка отписки от автора поста."""
        following_user = User.objects.create(username="following")
        Follow.objects.create(user=self.user, author=following_user)
        self.authorized_client.get(reverse("posts:profile_unfollow",
                                           kwargs={'username':
                                                   following_user}))
        self.assertFalse(Follow.objects.filter(user=self.user,
                                               author=following_user).exists())

    def test_follow_user_followers(self):
        """Проверка наличия подписки у позьзователя-подписчика."""
        Follow.objects.create(user=self.user, author=self.post.author)
        response = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertIn(self.post, response.context["page_obj"])

    def test_follow_user_unfollow(self):
        """Проверка отсутствия подписки у позьзователя-не подписчика."""
        outsider = User.objects.create(username="user_1")
        self.authorized_client.force_login(outsider)
        response = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertNotIn(self.post, response.context["page_obj"])


class PaginatorViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="auth")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
        )
        self.reverse_adress = [
            reverse("posts:index"),
            reverse(
                "posts:group_list", kwargs={"slug": self.group.slug}),
            reverse(
                "posts:profile", kwargs={"username": self.user}
            ),
        ]
        test_post: list = []
        for i in range(TEST_OF_POST):
            test_post.append(Post(text=f'Тестовый текст {i}',
                                  group=self.group,
                                  author=self.user))
        Post.objects.bulk_create(test_post)

    def test_first_page_contains_ten_records(self):
        """Количество постов на странице соответствует Paginator."""
        for adress in self.reverse_adress:
            with self.subTest(adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(len(response.context["page_obj"]),
                                 settings.ENTRIES_THE_PAGE)

    def test_second_page_contains_three_records(self):
        """Остаток постов на второй стрпанице."""
        for adress in self.reverse_adress:
            with self.subTest(adress):
                response = self.authorized_client.get(adress + '?page=2')
                self.assertEqual(len(response.context["page_obj"]),
                                 OBJECTS_TWO_PAGES)
