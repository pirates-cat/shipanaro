import os

SHIPANARO_API_GROUP = "system"
SHIPANARO_SITE_NAME = "Pirates de Catalunya"
SHIPANARO_SITE_URL = os.getenv("SHIPANARO_SITE_URL", "https://tripulacio.pirates.cat")
SHIPANARO_AUTH_PASSWORD_RESET_FORM = "humans.auth.forms.PasswordResetForm"

SSO_SECRET_KEY = os.getenv("SHIPANARO_SSO_SECRET_KEY", None)
SSO_LOGIN_URL = "https://debat.pirates.cat/session/sso_login"
SSO_AUTOMATIC_GROUPS = "militants"
