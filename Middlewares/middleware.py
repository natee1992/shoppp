import json

from django.utils.deprecation import MiddlewareMixin
from django.http.multipartparser import MultiPartParser

from Api.utils import params_errors


class MethodConvertMiddleware(MiddlewareMixin):
    '''自定义method方法'''

    def process_request(self, request):
        method = request.method
        if 'application/json' in request.META['CONTENT_TYPE']:
            try:
                data = json.loads(request.body.decode())
                files = None
            except Exception as e:
                return params_errors({
                    'msg': '请求数据格式错误'
                })
        elif 'multipart/form-data' in request.META['CONTENT_TYPE']:
            data, files = MultiPartParser(
                request.META, request, request.META.upload_handlers).parse()
        else:
            data = request.GET
            files = None
        if 'HTTP_X_METHOD' in request.META:
            method = request.META['HTTP_X_METHOD'].upper()
            setattr(request, 'method', method)
        if files:
            setattr(request, '{method}_FILES'.format(method=method), files)
        setattr(request, method, data)
