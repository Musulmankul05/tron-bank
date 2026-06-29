from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

class TwoFactorRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *request_args, **request_kwargs):
        if not getattr(request.user, 'totp_secret', None):
            return redirect('users:setup2fa')
        return super().dispatch(request, *request_args, **request_kwargs)