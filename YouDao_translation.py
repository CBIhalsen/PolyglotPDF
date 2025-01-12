import uuid
import requests
import hashlib
import time
import json
import load_config
import traceback  # 添加这个以获取详细的错误堆栈


def translate(texts, target_lang):
    YOUDAO_URL = 'https://openapi.youdao.com/v2/api'
    print('hh')
    print(texts)

    try:
        config = load_config.load_config()
        credentials = config['translation_services']['youdao']

        print("配置信息:", config)  # 打印配置信息
        print("凭证信息:", credentials)  # 打印凭证信息

    except Exception as e:
        print("配置加载错误:", str(e))
        print(traceback.format_exc())
        return None

    def encrypt(sign_str):
        try:
            hash_algorithm = hashlib.sha256()
            hash_algorithm.update(sign_str.encode('utf-8'))
            return hash_algorithm.hexdigest()
        except Exception as e:
            print("加密错误:", str(e))
            print(traceback.format_exc())
            return None

    def truncate(q):
        if q is None:
            return None
        size = len(q)
        return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]

    def do_request(data):
        try:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            print("请求URL:", YOUDAO_URL)  # 打印请求URL
            print("请求数据:", data)  # 打印请求数据
            response = requests.post(YOUDAO_URL, data=data, headers=headers)
            print("响应状态码:", response.status_code)  # 打印响应状态码
            print("响应内容:", response.text)  # 打印响应内容
            return response
        except Exception as e:
            print("请求错误:", str(e))
            print(traceback.format_exc())
            return None

    try:
        # 确保输入文本为列表格式
        if isinstance(texts, str):
            texts = [texts]

        print("输入文本:", texts)  # 打印输入文本

        # 准备请求数据
        data = {
            'from': 'auto',
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
        print('回复')
        print(response)
        if response is None:
            print("API请求失败")
            return None

        response_data = json.loads(response.content.decode("utf-8"))
        print("API响应数据:", response_data)  # 打印完整的响应数据

        # 检查响应中是否包含错误信息
        if 'errorCode' in response_data and response_data['errorCode'] != '0':
            print(f"API返回错误: {response_data.get('errorCode')}")
            return None

        # 修改翻译结果的提取方式
        if 'translateResults' in response_data:
            translations = []
            for result in response_data['translateResults']:
                if isinstance(result, dict) and 'translation' in result:
                    translations.append(result['translation'])
                else:
                    translations.append(str(result))

            return translations
        else:
            print("响应数据中没有 translateResults 字段")
            # 尝试其他可能的响应格式
            if 'translation' in response_data:
                return response_data['translation']
            return None

    except Exception as e:
        print(f"翻译过程错误: {str(e)}")
        print(f"详细错误信息: {traceback.format_exc()}")
        return None


# 使用示例:
if __name__ == '__main__':
    # 认证信息


    # 要翻译的文本
    texts = ["很久很久以前", "待输入的文字2", "待输入的文字3"]

    # 目标语言
    target_lang = 'en'

    # 调用翻译
    results = translate(texts, target_lang)

    if results:
        for original, translated in zip(texts, results):
            print(f"原文: {original}")
            print(f"译文: {translated}\n")
