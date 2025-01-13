import requests
import json
import load_config

config = load_config.load_config()

API_KEY = config['translation_services']['baidu']['api_key']
SECRET_KEY = config['translation_services']['baidu']['secret_key']


def translate_batch(original_lang,target_lang,text_list):
    """
    批量翻译文本
    :param text_list: 要翻译的文本列表
    :return: 翻译结果列表
    """
    url = "https://aip.baidubce.com/rpc/2.0/mt/texttrans/v1?access_token=" + get_access_token()

    # 将文本列表用\n连接成一个字符串
    text_to_translate = "\n".join(text_list)

    payload = json.dumps({
        "from": original_lang,
        "to": target_lang,
        "q": text_to_translate
    })

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    result = response.json()

    # 返回翻译结果
    if 'result' in result and 'trans_result' in result['result']:
        return [item['dst'] for item in result['result']['trans_result']]
    return []


def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))


def batch_translate(text_list,original_lang,target_lang ):
    """
    分批处理大量文本
    :param text_list: 要翻译的完整文本列表
    :param batch_size: 每批处理的文本数量
    :return: 所有译文列表
    """
    batch_size = 10
    all_translations = []
    for i in range(0, len(text_list), batch_size):
        batch = text_list[i:i + batch_size]
        translations = translate_batch(original_lang=original_lang,target_lang=target_lang,text_list=text_list)
        all_translations.extend(translations)
    return all_translations


def translate(texts, original_lang,target_lang):
    # 示例输入列表
    # texts_to_translate = ['Hello Boys', 'Go home', "We can beat them"]

    # 获取翻译结果
    translated_texts = batch_translate(text_list=texts,original_lang=original_lang,target_lang=target_lang)

    # 返回翻译结果列表

    return translated_texts


# if __name__ == '__main__':
#     translate()
