from django.conf import settings
import importlib


def import_setting_class(name, default=None):
    setting_class = default
    custom = getattr(settings, name, None)
    if custom:
        data = custom.split('.')
        module_name = '.'.join(data[0:-1])
        module = importlib.import_module(module_name)
        setting_class = getattr(module, data[-1])
    return setting_class
