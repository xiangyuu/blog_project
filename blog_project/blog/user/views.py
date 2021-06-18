import json
import jwt
from django.http import JsonResponse
from django.shortcuts import render
from .models import *
import hashlib
import time
import base64
from btoken.views import *
from tools.login_check import login_check
# Create your views here.
@login_check('PUT')
def users(request,username=None):
    if request.method=='GET':
        if username:
            try:
                user=UserProfile.objects.get(username=username)
            except Exception as e:
                user=None
            if not user:
                result={'code':208,'error':'no user!'}
                return JsonResponse(result)
            if  request.GET.keys():
                data={}
                for k in request.GET.keys():
                    if hasattr(user,k):
                        v=getattr(user,k)
                        if k=='avatar':
                            data[k]=str(v)
                        else:
                            data[k]=v
                result={'code':200,'username':username,'data':data}
                return JsonResponse(result)


            else:
                result=({'code':200,'username':username,'data':{'nickname':user.nickname,'sign':user.sign,'info':user.info,
                                 'avatar':str(user.avatar)}})
                return JsonResponse(result)
        else:
            return JsonResponse({'code': 200,'error':'GET'})
    elif request.method=='POST':
        json_str=request.body
        if not json_str:
            result={'code':201,'error':'please give me data!'}
            return JsonResponse(result)
        json_obj=json.loads(json_str)
        username=json_obj.get('username')
        if not username:
            result = {'code': 202, 'error': 'please give me username!'}
            return JsonResponse(result)
        email=json_obj.get('email')
        if not email:
            result={'code':203,'error':'please give me email!'}
            return JsonResponse(result)
        password_1=json_obj.get('password_1')
        password_2=json_obj.get('password_2')
        if not password_1 or not password_2:
            result={'code':204,'error':'please give me password!'}
            return JsonResponse(result)
        if password_2 != password_1:
            result={'code':205,'error':'your password not same!'}
            return JsonResponse(result)
        old_user=UserProfile.objects.filter(username=username)
        if old_user:
            result={'code':206,'error':'your username is already existed!'}
            return JsonResponse(result)
        md5=hashlib.md5()
        md5.update(password_1.encode())
        sign=info=''
        try:
            UserProfile.objects.create(
                username=username,
                nickname=username,
                email=email,
                password=md5.hexdigest(),
                sign=sign,
                info=info
            )
        except Exception as e:
            result={'cdoe':207,'error':'server is busy!'}
            return JsonResponse(result)
        token=make_token(username)
        result={'code':200,'username':username,'data':{'token':token.decode()}}
        return JsonResponse(result)
    elif request.method=='PUT':
        user=request.user
        json_str=request.body
        if not json_str:
            result={'code':209,'error':'please give me json!'}
            return JsonResponse(request)
        json_obj=json.loads(json_str)

        if 'sign' not in json_obj:
            result={'code':210,'error':'no sign!'}
            return JsonResponse(result)
        if 'info' not in json_obj:
            result={'code':211,'error':'no info!'}
            return JsonResponse(result)
        sign=json_obj.get('sign')
        info=json_obj.get('info')
        request.user.sign=sign
        request.user.info=info
        request.user.save()
        result={'code':200,'username':request.user.username}
        return JsonResponse(result)

@login_check('POST')
def user_avatar(request,username):
    if request.method!='POST':
        result={'code':212,'error':'I need POST!'}
        return JsonResponse(result)
    avatar=request.FILES.get('avatar')
    if not avatar:
        result={'code':213,'error':'I need avatar!'}
        return JsonResponse(result)

    request.user.avatar=avatar
    request.user.save()
    result={'code':200,'username':request.user.username}
    return JsonResponse(result)




























