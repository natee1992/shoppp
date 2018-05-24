import json

from django.http.response import HttpResponse
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from Api.utils import method_not_allowed


class Resource(object):
    def __init__(self, name=None):
        self.name = name or self.__class__.__name__.upper()

    def enter(self, request, *args, **kwargs):
        method = request.method
        if method == 'GET':
            response = self.get(request, *args, **kwargs)
        elif method == 'POST':
            response = self.post(request, *args, **kwargs)
        elif method == 'PUT':
            response = self.put(request, *args, **kwargs)
        elif method == 'DELETE':
            response = self.delete(request, *args, **kwargs)
        elif method == 'OPTION':
            response = self.option(request, *args, **kwargs)
        elif method == 'HEAD':
            response = self.head(request, *args, **kwargs)
        else:
            return HttpResponse(
                json.dumps({
                    'state': 422,
                    'msg': '方法不支持'
                }),
                content_type='application/json')
        return response

    def get(self, request, *args, **kwargs):
        return method_not_allowed()

    def post(self, request, *args, **kwargs):
        return method_not_allowed()

    def put(self, request, *args, **kwargs):
        return method_not_allowed()

    def option(self, request, *args, **kwargs):
        return method_not_allowed()

    def head(self, request, *args, **kwargs):
        return method_not_allowed()

    def delete(self, request, *args, **kwargs):
        return method_not_allowed()


# url注册
class Register(object):
    def __init__(self, version='v1', *args, **kwargs):
        self.version = version
        self.resources = []

    def regist(self, resource):
        self.resources.append(resource)

    @property
    def urls(self):
        urlpatterns = []
        for resource in self.resources:
            urlpatterns.append(
                url(r'^{version}/{name}/$'.format(
                    version=self.version, name=resource.name),
                    csrf_exempt(resource.enter)))
        return urlpatterns
