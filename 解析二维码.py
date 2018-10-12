import requests

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36',
}
response = requests.post(url='http://jiema.wwei.cn/fileupload.html?op=jiema&token=0e7f22d06d0206dd4de9890d5bd5619ca5828a0e',
                         files={'file': ('1.jpg', open('1.jpg', 'rb'))}, headers=headers)
print(response)
print(response.text)
