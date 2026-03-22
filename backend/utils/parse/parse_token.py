# -*- coding: utf-8 -*-
import json
import base64


def base64_url_decode(inp):
    padding = '=' * (4 - (len(inp) % 4))
    return base64.urlsafe_b64decode(inp + padding)


def parse_token(token_str: str):
    """ 根据id_token解析用户信息 """
    header, payload, signature = token_str.split('.')
    return {"header": json.loads(base64_url_decode(header)), "payload": json.loads(base64_url_decode(payload))}


if __name__ == '__main__':
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibmFtZSI6Ilx1N2JhMVx1NzQwNlx1NTQ1OCIsInJvbGVfbGlzdCI6WzEsMl0sImFwaV9wZXJtaXNzaW9ucyI6WyJhZG1pbiJdLCJidXNpbmVzc19saXN0IjpbMSwyLDMsNCw1LDYsNyw5LDEwLDExLDEyXSwiZXhwIjoxNzAyMzgxMDI3LjcwMzkzNn0.F_tZqYCX2MFkDk-Gdx5rPwA2QpI9_pDpoqjnVm9n7L0'
    print(parse_token(token))
