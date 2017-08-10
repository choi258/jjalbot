# -*- coding: utf-8 -*-
from flask import Flask, request, Response
import requests
from collections import defaultdict
import re
import json

app = Flask(__name__)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1;) Gecko/20100101 Firefox/13.0.1'}
IMG_MAX_HASH = 10

predicate_dict = defaultdict(list)

@app.route('/slack', methods=['POST'])
def inbound():
    keyword = request.form.get('text').encode("utf-8")
    img_url = get_jjal(keyword)
    json_data = {
        "response_type": "in_channel",
        "text": img_url
    }
    return Response(json.dumps(json_data), mimetype='application/json')


def get_jjal(keyword):
    print 'keyword: ' + str(keyword)
    url = 'https://www.google.com/search?q=' + keyword + '&source=lnms&tbm=isch&tbs=isz:m,ift:jpg&safe=active'
    response = requests.get(url, headers=HEADERS)
    # print response.content
    img_url_list = retrieve_img_url(response.content)

    pick_url = pick_jjal_return_url(img_url_list, keyword)

    return pick_url


def retrieve_img_url(dirty_string):
    regex_json = re.compile('\>({.*?})\<')
    json_list = regex_json.findall(dirty_string)
    img_url_list = []

    for json_string in json_list:
        img_url_list.append(json.loads(json_string)['ou'])

    return img_url_list


# to avoid duplicate
def pick_jjal_return_url(img_url_list, keyword):

    keyword_len = len(predicate_dict[keyword])

    hash_index = keyword_len % IMG_MAX_HASH
    print 'hash_index: ' + str(hash_index)
    predicate_dict[keyword].append(img_url_list[hash_index])
    return img_url_list[hash_index]


@app.route('/', methods=['GET'])
def test():
    return Response('It works!')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
