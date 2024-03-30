
import tiktoken
import time

import os
import Deepl_Translation as dt

os.environ['TRANSFORMERS_OFFLINE']="1"
# #
# Get the encoder of a specific model, assume gpt3.5, tiktoken is extremely fast,
# and the error of this statistical token method is small and can be ignored
enc = tiktoken.encoding_for_model("gpt-3.5")


class Offline_translation:

    def __init__(self,original_language,target_language,texts_to_process=[]):

        self.model_name = f"opus-mt-{original_language}-{target_language}"
        self.original_text = texts_to_process
        self.original_language = original_language
        self.target_language = target_language


    def translation(self):
        processed_texts= process_texts(self.original_text,enc)
        split_points = calculate_split_points(processed_texts)
        translated_texts = batch_translate(processed_texts=processed_texts, split_points=split_points,original_language=self.original_language,target_language=self.target_language)

        return translated_texts

class Online_translation:


    def __init__(self,original_language,target_language,key_deepl,texts_to_process=[]):

        self.model_name = f"opus-mt-{original_language}-{target_language}"
        self.original_text = texts_to_process
        self.target_language = target_language
        self.api_key_deepl = key_deepl


    def deepl_translation(self):

        translated_texts = dt.translate(self.original_text,self.target_language,self.api_key_deepl)

        return translated_texts




t = time.time()
def split_text_to_fit_token_limit(text, encoder, index_text, max_length=280):
    tokens = encoder.encode(text)
    if len(tokens) <= max_length:
        return [(text, len(tokens), index_text)]  # Return text along with its token count and original index 返回文本及其标记计数和原始索引

    # Pre-calculate possible split points (spaces, periods, etc.)
    split_points = [i for i, token in enumerate(tokens) if encoder.decode([token]).strip() in [' ', '.', '?', '!','！','？','。']]
    parts = []
    last_split = 0
    for i, point in enumerate(split_points + [len(tokens)]):  # Ensure the last segment is included
        if point - last_split > max_length:
            part_tokens = tokens[last_split:split_points[i - 1]]
            parts.append((encoder.decode(part_tokens), len(part_tokens), index_text))
            last_split = split_points[i - 1]
        elif i == len(split_points):  # Handle the last part
            part_tokens = tokens[last_split:]
            parts.append((encoder.decode(part_tokens), len(part_tokens), index_text))

    return parts

def process_texts(texts, encoder):
    processed_texts = []
    for i, text in enumerate(texts):
        sub_texts = split_text_to_fit_token_limit(text, encoder, i)
        processed_texts.extend(sub_texts)
    return processed_texts



def calculate_split_points(processed_texts, max_tokens=425):
    split_points = []  # 存储划分点的索引
    current_tokens = 0  # 当前累积的token数

    for i in range(len(processed_texts) - 1):  # 遍历到倒数第二个元素
        current_tokens = processed_texts[i][1]
        next_tokens = processed_texts[i + 1][1]

        # 如果当前元素和下一个元素的token数之和超过了限制
        if current_tokens + next_tokens > max_tokens:
            split_points.append(i)  # 当前元素作为一个划分点
        # 注意：这里不需要重置 current_tokens，因为每次循环都是新的一对元素

    # 最后一个元素总是一个划分点，因为它后面没有元素与之相邻
    split_points.append(len(processed_texts) - 1)

    return split_points


def translate(texts,original_language,target_language):
    # 这里仅返回相同的文本列表作为示例，实际中应返回翻译后的文本
    from transformers import pipeline, AutoTokenizer

    model_name = f"./opus-mt-{original_language}-{target_language}"  # 请替换为实际路径
    # 创建翻译管道，指定本地模型路径
    pipe = pipeline("translation", model=model_name)
    # 获取tokenizer，指定本地模型路径
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    result = pipe(texts)
    # print(result)
    # 原始列表

    # 提取值并组合成新的列表
    result_values = [d['translation_text'] for d in result]
    # print(result_values)
    # print(texts,"列1")
    print(texts,'TT')
    print(result_values,"TTT")
    return result_values



def batch_translate(processed_texts, split_points,original_language,target_language):
    translated_texts = []  # 存储翻译后的文本的列表
    index_mapping = {}  # 存储每个int_value对应在translated_texts中的索引

    start_index = 0  # 当前批次的起始索引

    # 遍历划分点，按批次翻译文本
    for split_point in split_points:
        # 提取当前批次的文本（不包括划分点的下一个元素）
        batch = processed_texts[start_index:split_point + 1]
        batch_texts = [text for text, _, _ in batch]
        # 翻译函数
        translated_batch = translate(texts=batch_texts,original_language=original_language,target_language=target_language)

        # 遍历当前批次的翻译结果
        for translated_text, (_, _, int_value) in zip(translated_batch, batch):
            if int_value in index_mapping:
                # 如果键已存在，将新的翻译文本与原有的值拼接
                translated_texts[index_mapping[int_value]] += " " + translated_text
            else:
                # 如果键不存在，直接添加到列表，并记录其索引
                index_mapping[int_value] = len(translated_texts)
                translated_texts.append(translated_text)

        # 更新下一批次的起始索引
        start_index = split_point + 1

    return translated_texts

