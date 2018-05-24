import json

from django.http.response import HttpResponse


def json_response(data):
    return HttpResponse(json.dumps({
        'state': 200,
        'msg': 'ok',
        'data': data
    }), content_type='application/json')


def method_not_allowed():
    return HttpResponse(json.dumps({
        'state': 405,
        'msg': '方法不支持'
    }), content_type='application/json')