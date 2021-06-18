import html
import json

from django.http import JsonResponse
from django.shortcuts import render
from user.models import *
from tools.login_check import *
from topic.models import *
import jwt
from message.models import *
# Create your views here.

@login_check('POST','DELETE')
def topics(request,author_id):
    if request.method=='GET':
        authors = UserProfile.objects.filter(username=author_id)
        if not authors:
            result = {'code': 308, 'error': 'No author!'}
            return JsonResponse(result)
        author = authors[0]
        visit = get_user_by_request(request)
        visit_name = None
        if visit:
            visit_name = visit.username

        if request.GET.get('t_id'):
            t_id = request.GET.get('t_id')
            t_id=int(t_id)
            is_self=False
            if visit_name == author_id:
                is_self = True
                try:
                    author_topic = Topic.objects.get(author_id=author_id, id=t_id)
                except:
                    result={'code':312,'error':'No topic!'}
                    return JsonResponse(result)
                res=make_topic_res(author,author_topic,is_self)

            else:
                try:
                    visit_topic = Topic.objects.get(author_id=author_id, id=t_id, limit='public')
                except:
                    result={'code':313,'error':'No topic!'}
                    return JsonResponse(result)
                res=make_topic_res(author,visit_topic,is_self)
            return JsonResponse(res)

        else:

            category=request.GET.get('category')
            if category in ['tec','no-tec']:
                if visit_name==author_id:
                    if category in 'tec':
                        topics=Topic.objects.filter(author_id=author_id,category=category)
                    else:
                        topics=Topic.objects.filter(author_id=author_id,category=category)
                else:
                    if category in 'tec':
                        topics=Topic.objects.filter(author_id=author_id,category=category,limit='public')
                    else:
                        topics=Topic.objects.filter(author_id=author_id,category=category,limit='public')
            else:
                    if visit_name==author_id:
                        topics=Topic.objects.filter(author_id=author_id)
                    else:
                        topics = Topic.objects.filter(author_id=author_id,limit='public')

            res=make_topics_res(author,topics)
            return JsonResponse(res)


    elif request.method=='POST':
        json_str=request.body
        if not json_str:
            result={'code':301,'error':'Please give me json!'}
            return JsonResponse(result)
        json_obj=json.loads(json_str)
        title=json_obj.get('title')
        title=html.escape(title)
        if not title:
            result={'code':302,'error':'Please give me title!'}
            return JsonResponse(result)
        category=json_obj.get('category')
        if category not in ['tec','no-tec']:
            result={'code':303,'error':'your category is wrong!'}
            return JsonResponse(result)
        limit=json_obj.get('limit')
        if limit not in ['public','private']:
            result={'code':304,'error':'your limit is wrong!'}
            return JsonResponse(result)
        content=json_obj.get('content')
        if not content:
            result={'code':305,'error':'Please give me content!'}
        content_text=json_obj.get('content_text')
        if not content_text:
            result={'code':306,'error':'Please give me content_text!'}
            return JsonResponse(result)
        introduce=content_text[:30]
        topic=Topic.objects.create(
            title=title,
            category=category,
            limit=limit,
            content=content,
            introduce=introduce,
            author=request.user
        )
        result={'code':200,'username':request.user.username}
        return JsonResponse(result)


    elif request.method=='DELETE':
        token_name=request.user.username
        if token_name!=author_id:
            result={'code':309,'error':'you can not do it!'}
            return JsonResponse(result)
        topic_id=request.GET.get('topic_id')
        try:
            topic=Topic.objects.get(id=topic_id)
        except:
            result={'code':310,'error':'you can not do it!'}
            return JsonResponse(result)

        if topic.author.username!=author_id:
            result={'code':311,'error':'you can not do it!'}
            return JsonResponse(result)
        topic.delete()
        result={'code':200}
        return JsonResponse(result)








    return JsonResponse({'code':200,'error':'test'})





def make_topics_res(author,topics):
    res={'code':200,'data':{}}
    data={}
    data['nickname']=author.nickname
    topic_list=[]
    for topic in topics:
        d={}
        d['id']=topic.id
        d['title']=topic.title
        d['category']=topic.category
        d['created_time']=topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
        d['content']=topic.content
        d['introduce']=topic.introduce
        d['author']=author.nickname
        topic_list.append(d)
    data['topics']=topic_list
    res['data']=data
    return res

def make_topic_res(author,author_topic,is_self):
    if is_self:
        next_topic=Topic.objects.filter(author_id=author_topic.author_id,id__gt=author_topic.id).first()
        last_topic=Topic.objects.filter(author_id=author_topic.author_id,id__lt=author_topic.id).last()

    else:
        next_topic = Topic.objects.filter(author_id=author_topic.author_id,limit='public', id__gt=author_topic.id).first()
        last_topic = Topic.objects.filter(author_id=author_topic.author_id,limit='public', id__lt=author_topic.id).last()
    if next_topic:
        next_topic_id = next_topic.id
        next_topic_title = next_topic.title
    else:
        next_topic_id = None
        next_topic_title = None
    if last_topic:
        last_topic_id=last_topic.id
        last_topic_title=last_topic.title
    else:
        last_topic_id=None
        last_topic_title=None


    message=Message.objects.filter(topic=author_topic).order_by('-created_time')
    msg_list=[]
    reply_dict={}
    msg_count=0
    for msg in message:
        msg_count+=1
        if msg.parent_message==0:
            msg_list.append({'id':msg.id,
                             'content':msg.content,
                             'publisher':msg.publisher.nickname,
                             'publisher_avatar':str(msg.publisher.avatar),
                             'created_time':msg.created_time.strftime('%Y-%m-%d %H:%M:%S'),
                             'reply':{}})
        else:
            reply_dict.setdefault(msg.parent_message,[])
            reply_dict[msg.parent_message].append({
                'msg_id':msg.id,
                'content':msg.content,
                'publisher':msg.publisher.nickname,
                'publisher_avatar':str(msg.publisher.avatar),
                'created_time':msg.created_time.strftime('%Y-%m-%d %H:%M:%S')
            })
    for _msg in msg_list:
        if _msg['id'] in reply_dict:
            _msg['reply']=reply_dict[_msg['id']]


    data = {}
    result={'code':200,'data':data}
    data['nickname']=author.nickname
    data['title']=author_topic.title
    data['category']=author_topic.category
    data['created_time']=author_topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
    data['content']=author_topic.content
    data['introduce']=author_topic.introduce
    data['author']=author_topic.author_id
    data['next_id']=next_topic_id
    data['next_title']=next_topic_title
    data['last_id']=last_topic_id
    data['last_title']=last_topic_title
    data['messages']=msg_list
    data['messages_count']=msg_count
    return result

