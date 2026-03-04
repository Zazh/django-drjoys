import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from django.views.generic import TemplateView

from orders.cart import merge_session_to_db
from orders.emails import send_welcome_email
from .forms import RegisterForm, LoginForm, ProfileForm


def _json_body(request):
    """Parse JSON body, falling back to POST data."""
    content_type = request.content_type or ''
    if 'application/json' in content_type:
        try:
            return json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return {}
    return request.POST


class RegisterView(View):

    @method_decorator(csrf_protect)
    def post(self, request):
        if request.user.is_authenticated:
            return JsonResponse(
                {'ok': False, 'errors': {'__all__': ['Вы уже авторизованы.']}},
                status=400,
            )
        data = _json_body(request)
        form = RegisterForm(data)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            merge_session_to_db(request)
            send_welcome_email(user)
            return JsonResponse({
                'ok': True,
                'data': {
                    'email': user.email,
                    'full_name': user.get_full_name(),
                },
            })
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


class LoginView(View):

    @method_decorator(csrf_protect)
    def post(self, request):
        if request.user.is_authenticated:
            return JsonResponse(
                {'ok': False, 'errors': {'__all__': ['Вы уже авторизованы.']}},
                status=400,
            )
        data = _json_body(request)
        form = LoginForm(data)
        if not form.is_valid():
            return JsonResponse({'ok': False, 'errors': form.errors}, status=400)

        user = authenticate(
            request,
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
        )
        if user is None:
            return JsonResponse(
                {'ok': False, 'errors': {'__all__': ['Неверный email или пароль.']}},
                status=401,
            )
        login(request, user)
        merge_session_to_db(request)
        return JsonResponse({
            'ok': True,
            'data': {
                'email': user.email,
                'full_name': user.get_full_name(),
                'phone': user.phone,
            },
        })


class LogoutView(View):

    @method_decorator(csrf_protect)
    def post(self, request):
        logout(request)
        return JsonResponse({'ok': True})


class ProfileView(View):

    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse(
                {'ok': False, 'errors': {'__all__': ['Требуется авторизация.']}},
                status=401,
            )
        user = request.user
        return JsonResponse({
            'ok': True,
            'data': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
                'phone': user.phone,
            },
        })

    @method_decorator(csrf_protect)
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse(
                {'ok': False, 'errors': {'__all__': ['Требуется авторизация.']}},
                status=401,
            )
        data = _json_body(request)
        form = ProfileForm(data, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'ok': True,
                'data': {
                    'email': request.user.email,
                    'full_name': request.user.get_full_name(),
                    'phone': request.user.phone,
                },
            })
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


class SSOCallbackView(TemplateView):
    """Popup callback page — sends postMessage to parent and closes."""

    template_name = 'accounts/sso_callback.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['sso_success'] = self.request.user.is_authenticated
        return ctx
