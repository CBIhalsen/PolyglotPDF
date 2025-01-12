import deepl
import load_config
def translate(texts,original_lang,target_lang):

# 你的 DeepL 授权密钥


    # 获取指定服务的认证信息


    config = load_config.load_config()

    auth_key = config['translation_services']['deepl']['auth_key']
    # print(auth_key)

    translator = deepl.Translator(auth_key)

    # 要翻译的文本列表


    # 翻译文本列表，目标语言设置为中文
    print(original_lang,target_lang)
    if original_lang == 'auto':
        results = translator.translate_text(texts, target_lang=target_lang)
    else:
        results = translator.translate_text(texts, source_lang=original_lang, target_lang=target_lang)


    # 初始化一个空列表来收集翻译结果
    translated_texts = []

    # 遍历翻译结果，将它们添加到列表中
    for result in results:
        translated_texts.append(result.text)
    return translated_texts



