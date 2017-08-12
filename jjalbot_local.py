# -*- coding: utf-8 -*-
from flask import Flask, request, Response
import requests
from collections import defaultdict
import re
import json
import grequests

app = Flask(__name__)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1;) Gecko/20100101 Firefox/13.0.1'}
WEBHOOK_URL = 'https://hooks.slack.com/services/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'
# IMG_MAX_SIZE = 60000
IMG_MAX_NUM = 10
img_url_dict = defaultdict(list)
keyword_index_dict = dict()


# http://127.0.0.1:5000/?keyword=%EC%86%90%EB%82%98%EC%9D%80

@app.route('/', methods=['GET', 'POST'])
def cache_img():
    keyword = request.args.get('keyword').encode("utf-8")
    print 'keyword: ' + str(keyword)
    pick_url = get_jjal(keyword)

    return Response(pick_url)


def get_jjal(keyword):
    url = 'https://www.google.com/search?q=' + keyword + '&source=lnms&tbm=isch&tbs=isz:m,ift:jpg&safe=active'

    # print response.content
    if not img_url_dict.has_key(keyword):
        response = requests.get(url, headers=HEADERS)
        img_url_list = retrieve_img_url(response.content)
        filtered_img_url_list = filter_img(img_url_list)
        if len(filtered_img_url_list) == 0:
            return None
        add_img_list_to_dict(filtered_img_url_list, keyword)
        keyword_index_dict[keyword] = 0

    pick_url = pick_jjal_return_url(keyword)

    return pick_url


def retrieve_img_url(dirty_string):
    regex_json = re.compile('\>({.*?})\<')
    json_list = regex_json.findall(dirty_string)
    img_url_list = []

    for json_string in json_list[:IMG_MAX_NUM]:
        img_url_list.append(json.loads(json_string)['ou'])

    return img_url_list


def add_img_list_to_dict(img_url_list, keyword):
    for img_url in img_url_list:
        img_url_dict[keyword].append(img_url)


def filter_img(img_url_list):
    rq = (grequests.head(img_url) for img_url in img_url_list)
    filtered_img_url_list = [i.request.url
                             for i in filter(lambda x: x.status_code == 200, grequests.map(rq))]

    return filtered_img_url_list


def isSuccess(img_url):
    r = requests.get(img_url)
    if r.status_code == 200:
        return True
    else:
        return False


def pick_jjal_return_url(keyword):
    keyword_index = keyword_index_dict[keyword]
    hash_index = keyword_index % len(img_url_dict[keyword])
    pick_img_url = img_url_dict[keyword][hash_index]

    print 'hash_index: ' + str(hash_index)
    keyword_index_dict[keyword] = keyword_index_dict[keyword] + 1

    return pick_img_url


@app.route('/', methods=['GET'])
def test():
    return Response('It works!')


if __name__ == '__main__':
    app.run(port=4081, debug=True)
