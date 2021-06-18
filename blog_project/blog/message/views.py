from django.http import JsonResponse
from django.shortcuts import render
from  tools.login_check import *
from topic.models import *
import json
from message.models import *
# Create your views here.

@login_check('POST')
def messages(request,topic_id):

    if request.method!='POST':
        result={'code':401,'error':'Please use POST!'}
        return JsonResponse(result)
    user=request.user
    json_str=request.body
    json_obj=json.loads(json_str)
    content=json_obj.get('content')
    if not content:
        result={'code':402,'error':'Please give me content!'}
        return JsonResponse(result)
    parent_id=json_obj.get('parent_id',0)

    try:
        topic=Topic.objects.get(id=topic_id)
    except:
        result={'code':403,'error':'No topic!'}
        return JsonResponse(result)

    if topic.limit=='private':
        if topic.author.username!=user.username:
            result={'code':404,'error':'Please get out!'}
            return JsonResponse(result)
    Message.objects.create(content=content,
                          publisher=user,
                          topic=topic,
                          parent_message=parent_id)
    result={'code':200,'data':{}}
    return JsonResponse(result)




