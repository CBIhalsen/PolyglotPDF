import time
import os
from .import Deepl_Translation as dt
from .import YouDao_translation as yt
from .import LLMS_translation as lt
import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
# #
# Get the encoder of a specific model, assume gpt3.5, tiktoken is extremely fast,
# and the error of this statistical token method is small and can be ignored


class Online_translation:
    def __init__(self, original_language, target_language, translation_type, texts_to_process=[]):
        self.model_name = f"opus-mt-{original_language}-{target_language}"
        self.original_text = texts_to_process
        self.target_language = target_language
        self.original_lang = original_language
        self.translation_type = translation_type

    def run_async(self, coro):
        # 往往只要 run_until_complete()，不手动 close() 即可
        return loop.run_until_complete(coro)

    def translation(self):
        print('translation api',self.translation_type)
        if self.translation_type == 'deepl':
            translated_list = self.deepl_translation()
        elif self.translation_type == 'youdao':
            translated_list = self.youdao_translation()
        elif self.translation_type == 'bing':
            # 使用同步包装器运行异步函数
            translated_list = self.run_async(self.bing_translation())
        elif self.translation_type == 'openai':
            # 使用同步包装器运行异步函数
            translated_list = self.run_async(self.openai_translation())
        elif self.translation_type == 'deepseek':
            # 使用同步包装器运行异步函数
            translated_list = self.run_async(self.deepseek_translation())
        elif self.translation_type == 'Doubao':
            # 使用同步包装器运行异步函数
            translated_list = self.run_async(self.Doubao_translation())
        elif self.translation_type == 'Qwen':
            # 使用同步包装器运行异步函数
            translated_list = self.run_async(self.Qwen_translation())
        elif self.translation_type == 'Grok':
            # 使用同步包装器运行异步函数
            translated_list = self.run_async(self.Grok_translation())
        elif self.translation_type == 'ThirdParty':
            # 使用同步包装器运行异步函数
            translated_list = self.run_async(self.ThirdParty_translation())
        elif self.translation_type == 'GLM':
            # 使用同步包装器运行异步函数
            translated_list = self.run_async(self.GLM_translation())
        else:
            translated_list = self.deepl_translation()

        return translated_list

    def deepl_translation(self):

        translated_texts = dt.translate(texts=self.original_text,original_lang=self.original_lang,target_lang=self.target_language)

        return translated_texts


    def youdao_translation(self):

        translated_texts = yt.translate(texts=self.original_text,original_lang=self.original_lang,target_lang=self.target_language)

        return translated_texts



    async def openai_translation(self):
        translator = lt.Openai_translation()
        translated_texts = await translator.translate(
            texts=self.original_text,
            original_lang=self.original_lang,
            target_lang=self.target_language
        )
        return translated_texts

    async def deepseek_translation(self):
        translator = lt.Deepseek_translation()
        translated_texts = await translator.translate(
            texts=self.original_text,
            original_lang=self.original_lang,
            target_lang=self.target_language
        )
        return translated_texts
    async def Doubao_translation(self):
        translator = lt.Doubao_translation()
        translated_texts = await translator.translate(
            texts=self.original_text,
            original_lang=self.original_lang,
            target_lang=self.target_language
        )
        return translated_texts
    async def Qwen_translation(self):
        translator = lt.Qwen_translation()
        translated_texts = await translator.translate(
            texts=self.original_text,
            original_lang=self.original_lang,
            target_lang=self.target_language
        )
        return translated_texts
    async def Grok_translation(self):
        translator = lt.Grok_translation()
        try:
            translated_texts = await translator.translate(
                texts=self.original_text,
                original_lang=self.original_lang,
                target_lang=self.target_language
            )
            print(f"Grok translation completed: {len(translated_texts)} texts processed")
            return translated_texts
        except Exception as e:
            print(f"Error in Grok translation: {e}")
            return [""] * len(self.original_text)

    async def ThirdParty_translation(self):
        translator = lt.ThirdParty_translation()
        try:
            translated_texts = await translator.translate(
                texts=self.original_text,
                original_lang=self.original_lang,
                target_lang=self.target_language
            )
            print(f"ThirdParty translation completed: {len(translated_texts)} texts processed")
            return translated_texts
        except Exception as e:
            print(f"Error in ThirdParty translation: {e}")
            return [""] * len(self.original_text)

    async def GLM_translation(self):
        translator = lt.GLM_translation()
        try:
            translated_texts = await translator.translate(
                texts=self.original_text,
                original_lang=self.original_lang,
                target_lang=self.target_language
            )
            print(f"GLM translation completed: {len(translated_texts)} texts processed")
            return translated_texts
        except Exception as e:
            print(f"Error in GLM translation: {e}")
            return [""] * len(self.original_text)

    async def bing_translation(self):
        translator = lt.Bing_translation()
        try:
            translated_texts = await translator.translate(
                texts=self.original_text,
                original_lang=self.original_lang,
                target_lang=self.target_language
            )
            print(f"Bing translation completed: {len(translated_texts)} texts processed")
            return translated_texts
        except Exception as e:
            print(f"Error in Bing translation: {e}")
            return [""] * len(self.original_text)


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


    # 提取值并组合成新的列表
    result_values = [d['translation_text'] for d in result]

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

