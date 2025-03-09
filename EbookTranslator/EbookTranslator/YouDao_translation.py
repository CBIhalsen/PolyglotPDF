import uuid
import requests
import hashlib
import time
import json


def translate(texts,original_lang, target_lang):
    """
    有道翻译API接口

    参数:
    texts: list, 要翻译的文本列表
    target_lang: str, 目标语言代码
    credentials: dict, 包含 app_key 和 app_secret 的字典

    返回:
    list: 翻译后的文本列表
    """
    YOUDAO_URL = 'https://openapi.youdao.com/v2/api'

    with open("config.json", 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 获取指定服务的认证信息
    if target_lang == 'zh':
        target_lang='zh-CHS'
    service_name = "youdao"
    credentials = config['translation_services'].get(service_name)
    if not credentials:
        raise ValueError(f"Translation service '{service_name}' not found in config")


    def encrypt(sign_str):
        hash_algorithm = hashlib.sha256()
        hash_algorithm.update(sign_str.encode('utf-8'))
        return hash_algorithm.hexdigest()

    def truncate(q):
        if q is None:
            return None
        size = len(q)
        return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]

    def do_request(data):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return requests.post(YOUDAO_URL, data=data, headers=headers)

    try:
        # 确保输入文本为列表格式
        if isinstance(texts, str):
            texts = [texts]

        print(type(texts))

        # 准备请求数据
        data = {
            'from': original_lang,
            'to': target_lang,
            'signType': 'v3',
            'curtime': str(int(time.time())),
            'appKey': credentials['app_key'],
            'q': texts,
            'salt': str(uuid.uuid1()),
            'vocabId': "您的用户词表ID"
        }

        # 生成签名
        sign_str = (credentials['app_key'] +
                    truncate(''.join(texts)) +
                    data['salt'] +
                    data['curtime'] +
                    credentials['app_secret'])
        data['sign'] = encrypt(sign_str)

        # 发送请求
        response = do_request(data)
        response_data = json.loads(response.content.decode("utf-8"))

        # 提取翻译结果
        translations = [result["translation"] for result in response_data["translateResults"]]
        print(translations)
        return translations

    except Exception as e:
        print(f"翻译出错: {str(e)}")
        return None
# 使用示例:
if __name__ == '__main__':
    # 认证信息


    # 要翻译的文本
    texts = ["hello", '待输入的文字"2', "待输入的文字3"]
    original_lang = 'auto'

    # 目标语言
    target_lang = 'zh'

    # 调用翻译
    results = translate(texts,original_lang='auto', target_lang=target_lang)
    print(results,'ggg')

    if results:
        for original, translated in zip(texts, results):
            print(f"原文: {original}")
            print(f"译文: {translated}\n")

