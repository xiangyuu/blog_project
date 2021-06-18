import json
from django.http import JsonResponse
from django.shortcuts import render
import hashlib
# Create your views here.
from user.models import *


def tokens(request):
    if not request.method=='POST':
        result={'code':101,'error':'please use POST!'}
        return JsonResponse(result)
    json_str=request.body
    if not json_str:
        result={'code':102,'error':'please give me json!'}
        return JsonResponse(result)
    json_obj=json.loads(json_str)

    username=json_obj.get('username')
    password=json_obj.get('password')
    if not username:
        result={'code':103,'error':'please give me username!'}
        return JsonResponse(result)
    if not password:
        result={'code':104,'error':'please give me password!'}
        return JsonResponse(result)

    user=UserProfile.objects.filter(username=username)
    if not user:
        result={'code':105,'error':'username or password is wrong!'}
        return JsonResponse(result)
    user=user[0]
    md5=hashlib.md5()
    md5.update(password.encode())
    if md5.hexdigest()!=user.password:
        result={'code':'106','error':'username or password is wrong!'}
        return JsonResponse(result)
    token=make_token(username)
    result={'code':200,'username':username,'data':{'token':token.decode()}}
    return JsonResponse(result)

def make_token(username,expire=3600*24):
    import jwt
    import time
    key='1125'
    now=time.time()
    payload={'username':username,'exp':now+expire}
    return jwt.encode(payload,key,algorithm='HS256')

