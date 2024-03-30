import deepl

def translate(texts,target_lang,auth_key):

# 你的 DeepL 授权密钥

    translator = deepl.Translator(auth_key)

    # 要翻译的文本列表


    # 翻译文本列表，目标语言设置为中文
    results = translator.translate_text(texts, target_lang=target_lang)

    # 初始化一个空列表来收集翻译结果
    translated_texts = []

    # 遍历翻译结果，将它们添加到列表中
    for result in results:
        translated_texts.append(result.text)
    return translated_texts





#
# texts = ["Hello, world!", "How are you?"]
# print(translate(texts,'zh'))