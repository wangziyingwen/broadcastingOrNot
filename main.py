# -*- coding: UTF-8 -*-
import os
import requests as req
import json,sys,random
from base64 import b64encode
from nacl import encoding, public

url_header=os.getenv('URL_HEADER')
gh_token=os.getenv('GH_TOKEN')
tg_bot=os.getenv('TGBOT').split(',')
tg_token=tg_bot[0]
chat_id=tg_bot[1]
up_on=os.getenv('UP_ON')
if up_on == '':
    up_on = r'{}'
on_list=json.loads(up_on)
gh_repo=os.getenv('GH_REPO')
ms_token=os.getenv('MS_TOKEN')
client_id=os.getenv('CLIENT_ID')
client_secret=os.getenv('CLIENT_SECRET')
focus_up=os.getenv('FOCUS_UP')
emailaddress=os.getenv('EMAIL')
time_set=os.getenv('TIME_SET')
htmlpath=sys.path[0]+r'/1.txt'
up_list=focus_up.split(',')
focus_up_add=os.getenv('FOCUS_UP_ADD').split(',')
focus_up_de=os.getenv('FOCUS_UP_DE').split(',')
if focus_up_add != ['']:
    for i in range(len(focus_up_add)):
        up_list.append(focus_up_add[i])
        focus_up=focus_up+','+focus_up_add[i]
        print('添加成功')
if focus_up_de != ['']:
    focus_up_1=''    
    for i in range(len(focus_up_de)):
        if focus_up_de[i] in up_list:
            up_list.remove(focus_up_de[i])
            print('删除成功')
    for i in range(len(up_list)):
        if i ==  len(up_list)-1:
            focus_up_1=focus_up_1+up_list[i]
        else:
            focus_up_1=focus_up_1+up_list[i]+','
    focus_up=focus_up_1                
broadcasting_list=''
broadcasting_list_4bot=''
Auth=r'token '+gh_token
geturl=r'https://api.github.com/repos/'+gh_repo+r'/actions/secrets/public-key'
puturl=r'https://api.github.com/repos/'+gh_repo+r'/actions/secrets/up_on'
key_id='wangziyingwen'
focus_list='Focus_list: '+'\n'
class Senderror(Exception):
    def __init__(self, arg):
        self.args = arg

def getmstoken():
    headers={
            'Content-Type':'application/x-www-form-urlencoded'
            }
    data={
         'grant_type': 'refresh_token',
         'refresh_token': ms_token,
         'client_id':client_id,
         'client_secret':client_secret,
         'redirect_uri':r'https://login.microsoftonline.com/common/oauth2/nativeclient',
         }
    for retry_ in range(4):
        html = req.post('https://login.microsoftonline.com/common/oauth2/v2.0/token',data=data,headers=headers)
        if html.status_code < 300:
            print(r'微软密钥获取成功')
            break
        else:
            if retry_ == 3:
                print(r'微软密钥获取失败')
    jsontxt = json.loads(html.text)       
    return jsontxt['access_token']
    
def sendEmail(content):
    headers={
            'Authorization': 'bearer ' + getmstoken(),
            'Content-Type': 'application/json'
            }
    mailmessage={
                'message':{
                          'subject': 'Broadcasting',
                          'body': {'contentType': 'HTML', 'content': content},
                          'toRecipients': [{'emailAddress': {'address': emailaddress}}],
                          },
                'saveToSentItems': 'true',
                }
    for retry_ in range(4):  
        posttext=req.post(r'https://graph.microsoft.com/v1.0/me/sendMail',headers=headers,data=json.dumps(mailmessage))
        if posttext.status_code < 300:
            print('邮件发送成功')
            break
        else:
            if retry_ == 3:
                print('邮件发送失败')
                raise Senderror('1')
    print('')

def getpublickey():
    #try:except?
    headers={
            'Accept': 'application/vnd.github.v3+json','Authorization': Auth
            }
    for retry_ in range(4):
        html = req.get(geturl,headers=headers)
        if html.status_code < 300:
            print("公钥获取成功")
            break
        else:
            if retry_ == 3:
                print("公钥获取失败，请检查secret里 GH_TOKEN 格式与设置是否正确")
    jsontxt = json.loads(html.text)
    public_key = jsontxt['key']
    global key_id 
    key_id = jsontxt['key_id']
    return public_key

def createsecret(public_key,secret_value):
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")

def setsecret(encrypted_value,url):
    headers={
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': Auth
            }
    data={
         'encrypted_value': encrypted_value,
         'key_id': key_id
         }
    #data_str=r'{"encrypted_value":"'+encrypted_value+r'",'+r'"key_id":"'+key_id+r'"}'
    for retry_ in range(4):
        putstatus=req.put(url,headers=headers,data=json.dumps(data))
        if putstatus.status_code < 300:
            print(r'secret上传成功')
            break
        else:
            if retry_ == 3:
                print(r'secret上传失败')        
    return putstatus

def deSecret(url):
    headers={
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': Auth
            }
    for retry_ in range(4):  
        posttext=req.delete(url,headers=headers)
        if posttext.status_code < 300:
             print('secret删除成功')
             break

def sendTgBot(content):
    headers={
            'Content-Type': 'application/json'
            }
    data={
         'chat_id':chat_id,
         'text':content,
         'parse_mode':'HTML'
         }  
    for retry_ in range(4):  
        posttext=req.post(r'https://api.telegram.org/bot'+tg_token+r'/sendMessage',headers=headers,data=json.dumps(data))
        if posttext.status_code < 300:
             print('tg推送成功')
             break
        else:
            if retry_ == 3:
                print('tg推送失败')
                raise Senderror('1')
    print('')
     
#判断是否更新关注
newornot = 0
for i in range(len(up_list)):
    if up_list[i] in on_list and len(up_list) == len(on_list):
        pass
    else:
        print('关注列表已更新')
        newornot=1
        on_list={}
        for _i in range(len(up_list)):
            on_list[up_list[_i]]=[0,0,0,0]
        break

print("总共url数 "+str(len(up_list))+'\n')
for i in range(len(up_list)):
    focus_list=focus_list+up_list[i]+' , '
    #获取信息
    for retry_ in range(4):
        upInfo_raw = req.get(url_header+r'rest/v1.0/search/performer/'+up_list[i])
        if upInfo_raw.status_code < 300:
            upInfo_response = json.loads(upInfo_raw.text)
        break
    for retry_ in range(4):
        streamInfo_raw = req.get(url_header+r'rest/v1.0/profile/'+up_list[i]+r'/streamInfo')
        if streamInfo_raw.status_code < 300:
            streamInfo_response = json.loads(req.get(url_header+r'rest/v1.0/profile/'+up_list[i]+r'/streamInfo').text)
            break
    print(up_list[i][0:2]+'***'+up_list[i][-1]+'   :')
    on_list[up_list[i]][1]=on_list[up_list[i]][1]+10
    on_list[up_list[i]][3]=on_list[up_list[i]][3]+10
    if on_list[up_list[i]][1] >= int(time_set):
        on_list[up_list[i]][0] = 0
        on_list[up_list[i]][1] = 0
    #每隔一个time_set清空一次数据
    if on_list[up_list[i]][3] >= int(time_set)*3:
        on_list[up_list[i]][3] = 0
    if 'online' in upInfo_response.keys():
        if upInfo_response['online'] == True:
            on_list[up_list[i]][0]=on_list[up_list[i]][0]+10
            on_list[up_list[i]][2]=on_list[up_list[i]][2]+10
            print("        on")
            if on_list[up_list[i]][0] == 10:
                #一个time_set区间发现on了并且没有发送过邮件，发送邮件
                if 'cdnURL' in streamInfo_response.keys():
                    broadcasting_list=broadcasting_list+r'<a href="'+url_header+up_list[i]+r'"> '+up_list[i]+r' </a>'+r'<a href="'+streamInfo_response['cdnURL']+r'"> cdn </a>'+'<br>'
                else:
                    print("        1 无法获取关键key，源码更新，需要修复")
                    broadcasting_list=broadcasting_list+r'<a href="'+url_header+up_list[i]+r'"> '+up_list[i]+r' </a> nUp<br>'
            if on_list[up_list[i]][2] == 10:
                if 'cdnURL' in streamInfo_response.keys():
                    broadcasting_list_4bot=broadcasting_list_4bot+r'<a href="'+url_header+up_list[i]+r'"> '+up_list[i]+r' </a>'+r'<a href="'+streamInfo_response['cdnURL']+r'"> cdn </a>'+'\n'
                else:
                    print("        2 无法获取关键key，源码更新，需要修复")
                    broadcasting_list_4bot=broadcasting_list_4bot+r'<a href="'+url_header+up_list[i]+r'"> '+up_list[i]+r' </a> nUp'+'\n'  
            elif on_list[up_list[i]][2] > 30:
                    on_list[up_list[i]][2]=0
        elif upInfo_response['online'] == False:
            if on_list[up_list[i]][2] !=0:
                on_list[up_list[i]][2]=0
            print("        off")
        else:
            print("        3 源码更新，需要修复")
    else:
        print("        4 源码更新，需要修复")
        if 'cdnURL' in streamInfo_response.keys():
            on_list[up_list[i]][0]=on_list[up_list[i]][0]+10
            on_list[up_list[i]][2]=on_list[up_list[i]][2]+10
            print("        on")
            if on_list[up_list[i]][0] == 10:
                #一个time_set区间发现on了并且没有发送过邮件，发送邮件
                broadcasting_list=broadcasting_list+r'<a href="'+url_header+up_list[i]+r'"> '+up_list[i]+r' </a>'+r'<a href="'+streamInfo_response['cdnURL']+r'"> cdn </a>'+'<br>'
            if on_list[up_list[i]][2] == 10:
                broadcasting_list_4bot=broadcasting_list_4bot+r'<a href="'+url_header+up_list[i]+r'"> '+up_list[i]+r' </a>'+r'<a href="'+streamInfo_response['cdnURL']+r'"> cdn </a>'+'\n'
            elif on_list[up_list[i]][2] > 30:
                on_list[up_list[i]][2]=0
        else:
            if on_list[up_list[i]][2] !=0:
                on_list[up_list[i]][2]=0
            print("        off")
    print('            '+str(on_list[up_list[i]]))
    
    
    
if broadcasting_list != '':
    sendEmail(r'<html><body>Who is broadcasting: <br>'+broadcasting_list+r'</body><html>')
if broadcasting_list_4bot != '':
    sendTgBot(r'Who is broadcasting: '+'\n'+broadcasting_list_4bot+'\n'+focus_list)

       
#上传新的on_list
public_key_1=getpublickey()
encrypted_value=createsecret(public_key_1,json.dumps(on_list))
setsecret(encrypted_value,r'https://api.github.com/repos/'+gh_repo+r'/actions/secrets/up_on')
if newornot == 1:
    encrypted_value=createsecret(public_key_1,focus_up)
    setsecret(encrypted_value,r'https://api.github.com/repos/'+gh_repo+r'/actions/secrets/focus_up')
if focus_up_de != '':
    deSecret(r'https://api.github.com/repos/'+gh_repo+r'/actions/secrets/focus_up_de')
if focus_up_add != '':
    deSecret(r'https://api.github.com/repos/'+gh_repo+r'/actions/secrets/focus_up_add')
