import requests, re, json, io, base64, os
from urllib.parse import quote
from bs4 import BeautifulSoup
from PIL import Image, PngImagePlugin

import requests
import time
import random
from hashlib import md5


def test_if_zhcn(string): # Check whether it contains Chinese
    for ch in string:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

def translate(kw): # Youdao Translation, time-sensitive, 24.4.20
	if test_if_zhcn(kw):
		#!/usr/bin/env python
		# -*- encoding: utf-8 -*-
		headers = {
    	'Cookie': 'OUTFOX_SEARCH_USER_ID=-690213934@10.108.162.139; OUTFOX_SEARCH_USER_ID_NCOO=1273672853.5782404; fanyi-ad-id=308216; fanyi-ad-closed=1; ___rl__test__cookies=1659506664755',
    	'Host': 'fanyi.youdao.com',
    	'Origin': 'https://fanyi.youdao.com',
    	'Referer': 'https://fanyi.youdao.com/',
    	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    	}
		lts = str(int(time.time() * 100))
		salt = lts + str(random.randint(0, 9))
		sign_data = 'fanyideskweb' + kw + salt +'Ygy_4c=r#e#4EX^NUGUc5'
		sign = md5(sign_data.encode()).hexdigest()
		data = {
			'i': kw,
			'from': 'AUTO',
			'to': 'AUTO',
			'smartresult': 'dict',
			'client': 'fanyideskweb',
			'salt':salt,
			'sign': sign,# encrypt
			'lts': lts,# timestamp
               
			# Encrypted data
			'bv': 'f0819a82107e6150005e75ef5fddcc3b',
			'doctype': 'json',
			'version': '2.1',
			'keyfrom': 'fanyi.web',
			'action': 'FY_BY_REALTlME',
		}
 
		# Obtain the resource address
		url = 'https://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
		response = requests.post(url, headers=headers, data=data)

		list_trans = response.text
		result = json.loads(list_trans)
		return result['translateResult'][0][0]['tgt']
	


def chatglm_json(prompt, history, max_length, top_p, temperature): # chatglm-API, 24.4.20
    url = "http://127.0.0.1:8000"
    payload = {
        "prompt": prompt,
        "history": history,
        "max_length": max_length,
        "top_p": top_p,
        "temperature": temperature
    }
    response = requests.post(url, json=payload)
    json_resp_raw = response.json()
    json_resp_raw_list = json.dumps(json_resp_raw)
    return json_resp_raw_list


def stable_diffusion(Pprompt,Nprompt): 
    # Call the SD module and pass in the input parameter as a forward and reverse prompt
    url = "http://127.0.0.1:7861"
    payload = {
        "prompt": Pprompt,
        "steps": 30,  # Depending on the sampler, it is generally 20~40
        "negative_prompt": Nprompt
    }
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    r = response.json()
    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
        png_payload = {
            "image": "data:image/png;base64," + i # Decode Base64 encoded image data
        }
        response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save('stable_diffusion.png', pnginfo=pnginfo)

