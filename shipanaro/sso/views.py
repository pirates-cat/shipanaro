from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.views import View
import base64
import hashlib
import hmac
import urllib


def login(request):
    payload = request.GET.get('sso', None)
    signature = request.GET.get('sig', None)
    if not payload or not signature:
        return HttpResponseBadRequest()
    digest = hmac.new(
        settings.SSO_SECRET_KEY.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(digest, signature):
        return HttpResponseBadRequest()
    request.session['nonce'] = base64.decodestring(payload.encode('utf-8')).decode('utf-8')
    return redirect('sso_auth')


@login_required
def authorize(request):
    nonce = request.session['nonce']
    payload = urllib.parse.urlencode({
        'external_id': request.user.pk,
        'email': request.user.email,
        'name': request.user.first_name,
        'username': request.user.username,
        'add_groups': settings.SSO_AUTOMATIC_GROUPS,
    })
    payload = '{}&{}'.format(
        nonce,
        payload,
    )
    payload = base64.b64encode(payload.encode('utf-8'))
    print(payload)
    signature = hmac.new(
        settings.SSO_SECRET_KEY.encode('utf-8'),
        payload,
        hashlib.sha256,
    ).hexdigest()
    url = '{}/?{}'.format(
        settings.SSO_LOGIN_URL,
        urllib.parse.urlencode({
            'sso': payload,
            'sig': signature,
        })
    )
    return redirect(url)
