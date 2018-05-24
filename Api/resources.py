import json

from django.http.response import HttpResponse

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
            resposne = self.head(request, *args, **kwargs)
        else:
            return HttpResponse(json.dumps({
                'msg': 422,
                'msg': '方法不支持'
            }), content_type='application/json')
        
    def get()
