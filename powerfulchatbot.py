#!/usr/bin/env python
# coding: utf-8

import command_dictionary


#包裝純文字格式
def package_text(unpackage_text):
    unpackage_text = 'text;'+unpackage_text
    return str(unpackage_text)


#包裝圖片格式
def package_img(unpackage_text):
    unpackage_text='img;'+unpackage_text
    return str(unpackage_text)


#包裝按鈕回應格式
def package_button_template(unpackage_text):
    unpackage_text='buttontemplate;'+unpackage_text
    return str(unpackage_text)


#獲得回應 （程式回傳點）
def get_reply(user_message,user_id=0):
    user_message = str(user_message)
    for command in command_dictionary.word.keys():
        if user_message.startswith(command):
            action_command = command_dictionary.word[command]
            reply=eval(action_command)
            return reply
    return talk_normal(user_message)


#獲得資料庫的指令
def get_MySql_command(user_MySql,user_message):
    for x in range(len(user_MySql)):
        if user_MySql[x] == '1':
            command_index=str(x)
            action_command=command_dictionary.word_MySQl[command_index]
            return eval(action_command)


#推薦吃什麼
def recommend_food(user_message):
    import re
    from bs4 import BeautifulSoup
    import requests
    import random
    from selenium import webdriver
    import os
    cities = ['台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市', '基隆市', '新竹市', '嘉義市', '新竹縣',
              '苗栗縣', '彰化縣', '南投縣', '雲林縣', '嘉義縣', '屏東縣', '宜蘭縣', '花蓮縣', '台東縣', '澎湖縣']

    try:
        if type(user_message) == str:
            url = 'https://www.foodpanda.com.tw/' + user_message
        else:
            lat = user_message.latitude
            lng = user_message.longitude
            address = user_message.address
            for c in cities:
                if re.search(c, address) != None:
                    city = c
            url = 'https://www.foodpanda.com.tw/restaurants/lat/' + str(lat) + '/lng/' + str(
                lng) + '/city/' + city + '/address/' + address
        print(url)
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'lxml')
        stores = []
        summarys = []
        costs = []
        pictures = []
        food_datas = {}
        for store in soup.find_all('span', 'name fn'):
            stores.append(store.text.replace(' ', ''))
        for summary in soup.find_all('li', 'vendor-characteristic'):
            summarys.append(summary.text[1:-1].replace('\n', ','))
        for cost in soup.find_all('ul', 'extra-info mov-df-extra-info'):
            costs.append(cost.text.replace('\n', '').replace(' ', ''))
        for picture in soup.find_all('div', 'vendor-picture b-lazy'):
            pictures.append(picture['data-src'].split('|')[0])
        for index, key in enumerate(stores):
            food_datas[key] = [summarys[index], costs[index], pictures[index]]
        which_one = random.randint(0, len(stores)-1)
        imageurl = food_datas[stores[which_one]][2]
        title = stores[which_one]
        text = food_datas[stores[which_one]][0] + '\n' + food_datas[stores[which_one]][1]
        label = '下一個'
        actionurl = url.replace('https://www.foodpanda.com.tw/', '')
    except:
        if type(user_message) == str:
            url = 'https://www.ipeen.com.tw/search/all/000/1-0-0-0/?adkw=' + user_message + '&so=sat'
        else:
            for c in cities:
                if re.search(c, address) != None:
                    x = c
            city = address[re.search(x[0], address).span()[0]:re.search('區', address).span()[1]]
            url = 'https://www.ipeen.com.tw/search/all/000/1-0-0-0/?adkw=' + city + '&so=sat'
        print(url)
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'lxml')
        stores = []
        summarys = []
        pictures = []
        for store in soup.find_all('a', {'data-label': '店名'}):
            stores.append(store.text.replace(' ', ''))
        for summary in soup.find_all('li', 'cate'):
            summarys.append(summary.text.replace('\xa0', '').replace('\n', '').replace(' ', ''))
        for picture in soup.find_all('img', 'lazy'):
            pictures.append(picture['src'])
        which_one = random.randint(0, len(stores)-1)
        print(which_one)
        imageurl = pictures[which_one]
        title = stores[which_one]
        text = summarys[which_one]
        label = '下一個'
        actionurl = url.replace('https://www.ipeen.com.tw/search/all/000/1-0-0-0/?adkw=', '').replace('&so=sat', '')
    reply = imageurl + ' ' + title + ' ' + text + ' ' + label + ' ' + actionurl
    reply = package_button_template(unpackage_text=reply)
    print(reply)
    return reply


# 查詢食物 第一次執行將資料庫某指令設為true
def set_MySqlfood(user_message,user_id):
    print('更新使用者食物查詢狀態:'+user_id)
    id=user_id
    import requests
    data={'id':id,'command':'recommend_food(user_message)'}
    r = requests.post('http://mumu.tw/mumu/php/Sara/SetCommand.php', data=data)
    print(r.text)
    reply='按左下角的+ 發送位置訊息給我 我就能推薦你食物呦！'
    reply=package_text(reply)
    print(reply)
    return reply


#推薦歌曲
def recommend_music():
    import json
    import random
    with open('./music.json', 'r') as load_f:
        song_datas = json.load(load_f)
    songs = []
    for key in song_datas.keys():
        songs.append(key)
    choose_one = songs[random.randint(0, len(song_datas)-1)]
    imageurl = song_datas[choose_one][1]
    title = song_datas[choose_one][0]
    text = song_datas[choose_one][3]
    label = 'MUSIC'
    actionurl = song_datas[choose_one][2]
    reply = imageurl + ' ' + title + ' ' + text + ' ' + label + ' ' + actionurl
    reply = package_button_template(unpackage_text=reply)
    return reply


def image_recognition(imagefilepath):
    reply=""
    import base64
    import json
    outputfile = 'data.json'
    requestlist = []
    feature_json_obj = []
    features = "FACE_DETECTION WEB_DETECTION"
    with open(imagefilepath, 'rb')as image_file:
        content_json_obj = {
            "content": base64.b64encode(image_file.read()).decode('UTF-8')
        }
    for word in features.split(' '):
        feature_json_obj.append({
            "type": word,
            "maxResults": "10"
        })

    requestlist.append({
        "features": feature_json_obj,
        "image": content_json_obj,
    })

    with open(outputfile, 'w') as output_file:
        json.dump({"requests": requestlist}, output_file)

    print('Send requests...')

    import requests
    data = open('./data.json', 'rb').read()
    response = requests.post(
        url='https://vision.googleapis.com/v1/images:annotate?key=',
        data=data,
        headers={'Content-Type': 'application/json'})
    response = response.text
    response_json = json.loads(response)
    face_response = response_json['responses'][0]
    peoplecount = 1
    emotions = ["喜悅 joyLikelihood", "難過 sorrowLikelihood", "生氣 angerLikelihood", "驚訝 surpriseLikelihood",
                "備感壓力 underExposedLikelihood", "憂鬱 blurredLikelihood", "戴帽子 headwearLikelihood"]
    compare_result = ["非常低的可能 VERY_UNLIKELY", "低可能 UNLIKELY", "可能 LIKELY", "非常可能 VERY_LIKELY","吻合 POSSIBLE"]
    if 'faceAnnotations' in response_json['responses'][0]:
        for face_result in face_response['faceAnnotations']:
            print('第', peoplecount, "個人看起來: \n")
            counttemp=str(peoplecount)
            reply += '第'+counttemp+"個人看起來: \n"
            for emotion in emotions:
                emotion_chinese = emotion.split(' ')[0]
                emotion_compare = emotion.split(' ')[1]
                for result in compare_result:
                    result_chinese = result.split(' ')[0]
                    result_compare = result.split(' ')[1]
                    if face_result[emotion_compare] == result_compare:
                        face_result[emotion_compare] = result_chinese
                print(emotion_chinese, ": ", face_result[emotion_compare])
                reply += str(emotion_chinese)+": "+str(face_result[emotion_compare])+"\n"
            peoplecount += 1
            print('\n')
            reply += '\n'
    else:
        reply+='你似乎給了我一張沒有人的照片呢 不過我還是幫你找一下網路上有沒有這張圖片\n'
    print('網頁分析')
    if 'fullMatchingImages' in response_json['responses'][0]['webDetection']:
        print(response_json['responses'][0]['webDetection']['fullMatchingImages'])
        print('\n')
        web_response_fullmatch = response_json['responses'][0]['webDetection']['fullMatchingImages']
        web_response_pagesmatch = response_json['responses'][0]['webDetection']['pagesWithMatchingImages']
        maxreply = 0
        for url in web_response_fullmatch:
            if(maxreply>5):
                break
            print("找到與圖片吻合的網址: ", url['url'])
            urltemp=str(url['url'])
            reply += "找到與圖片吻合的網址: "+urltemp+'\n'
            maxreply+=1
        maxreply = 0
        for url_item in web_response_pagesmatch:
            if (maxreply > 5):
                break
            print('找到有出現圖片的網站: '+url_item['url'])
            urltemp = str(url_item['url'])
            reply += '找到有出現圖片的網站:'+urltemp+'\n'
            maxreply += 1
    else:
        print('沒有圖片出現吻合的網站資料')
        reply+='沒有圖片出現吻合的網站資料'+'\n'
    if 'visuallySimilarImages' in response_json['responses'][0]['webDetection']:
        web_response_simullar = response_json['responses'][0]['webDetection']['visuallySimilarImages']
        simullar_max = 3  # 最多列出五個相似
        for items in web_response_simullar:
            if simullar_max <= 0:
                break
            else:
                print("找到與圖片相似的網站: ", items['url'])
                urltemp=str(items['url'])
                reply += "找到與圖片相似的網站: "+urltemp+'\n'
                simullar_max -= 1
    else:
        print('沒有相似圖片的網站資料')
        reply += '沒有相似圖片的網站資料'+'\n'

    reply=package_text(reply)
    return reply


def search_news():
    from bs4 import BeautifulSoup
    import requests
    res = requests.get('https://www.ettoday.net/news/news-list.htm')
    soup = BeautifulSoup(res.content,'html.parser')
    a_tags = soup.find_all("div", "part_list_2")
    title = ""
    html = "https://www.ettoday.net/news/news-list.htm/news/"
    reply=""
    range =0
    for tag in a_tags:
        if(range>3):
            break
        # 輸出超連結的文字
        if tag.find('a'):
            title = tag.find('a').text
            print(title)
            reply+=title+'\n'
            html=html+(tag.find('a').get('href'))
            print(html)
            reply+=html
            range+=1
    reply = package_text(reply)
    return reply
