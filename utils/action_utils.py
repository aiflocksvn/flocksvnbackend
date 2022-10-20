from django.apps import apps
from django.conf import settings
from django.contrib.admin.utils import NestedObjects
from django.db import router, models
from django.utils.text import capfirst


def get_third_party_model_name():
    system_apps = settings.THIRD_PARTY + settings.DEFAULT_APPS

    system_apps = list(map(lambda app_name: f'{app_name.split(".")[-1]}', system_apps))
    system_models = []
    for app in system_apps:
        try:
            models = list(map(lambda p: p.__name__, apps.get_app_config(app).get_models()))
            system_models = system_models + models
        except LookupError:
            pass
    return system_models


class CustomNestedObjects(NestedObjects):

    def collect(self, objs, source=None, source_attr=None, **kwargs):
        if type(objs) != list:
            model_name = objs.model.__name__
            if model_name in ignore_models:
                return
                # print(model_name)
        # print(model_name)
        for obj in objs:

            # print(obj)
            if source_attr and not source_attr.endswith('+'):
                related_name = source_attr % {
                    'class': source._meta.model_name,
                    'app_label': source._meta.app_label,
                }
                self.add_edge(getattr(obj, related_name), obj)
            else:
                self.add_edge(None, obj)
            self.model_objs[obj._meta.model].add(obj)
        try:
            return super(NestedObjects, self).collect(objs, source_attr=source_attr, **kwargs)
        except models.ProtectedError as e:
            self.protected.update(e.protected_objects)
        except models.RestrictedError as e:
            self.protected.update(e.restricted_objects)


def format_callback(obj):
    # model = obj.__class__
    opts = obj._meta
    return f'{capfirst(opts.verbose_name)} : {obj.__str__()}'


ignore_models = ['OutstandingToken',
                 'BlacklistedToken',
                 'APIKey',
                 'LogEntry',
                 'Permission',
                 'Group',
                 'ContentType',
                 'Session', 'Media']


def get_deleted_objects(objs, calc_model_count=False):
    """
    Find all objects related to ``objs`` that should also be deleted. ``objs``
    must be a homogeneous iterable of objects (e.g. a QuerySet).

    Return a nested list of strings suitable for display in the
    template with the ``unordered_list`` filter.
    """
    response = {}
    try:
        obj = objs[0]
    except IndexError:
        return [], {}, set(), []
    else:
        using = router.db_for_write(obj._meta.model)
    collector = CustomNestedObjects(using=using)
    collector.collect(objs)

    to_delete = collector.nested(format_callback)
    protected = [format_callback(obj) for obj in collector.protected]
    response['to_delete'] = to_delete
    response['protected'] = protected
    if calc_model_count:
        model_count = {
            model._meta.verbose_name_plural: len(objs)
            for model, objs in collector.model_objs.items()
        }
        response['model_count'] = model_count

    return response
