import asyncio
import aiohttp

from . import load_config

class Openai_translation:
    def __init__(self):
        config = load_config.load_config()
        self.api_key = config['translation_services']['openai']['auth_key']
        self.url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.model = config['translation_services']['openai']['model_name']

    async def translate_single(self, session, text, original_lang, target_lang):
        """单个文本的异步翻译"""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": f"You are a professional translator. Translate from {original_lang} to {target_lang}.Return only the translations"
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "response_format": {
                "type": "text"
            },
            "temperature": 0.3,
            "top_p": 0.9
        }

        try:
            async with session.post(self.url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content'].strip()
                else:
                    print(f"Error: {response.status}")
                    return ""
        except Exception as e:
            print(f"Error in translation: {e}")
            return ""

    async def translate(self, texts, original_lang, target_lang):
        """异步批量翻译"""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.translate_single(session, text, original_lang, target_lang)
                for text in texts
            ]
            return await asyncio.gather(*tasks)

class Deepseek_translation:
    def __init__(self):
        config = load_config.load_config()
        self.api_key = config['translation_services']['deepseek']['auth_key']
        self.url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.model = config['translation_services']['deepseek']['model_name']

    async def translate_single(self, session, text, original_lang, target_lang):
        """单个文本的异步翻译"""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": f"You are a professional translator. Translate from {original_lang} to {target_lang}.Return only the translations"
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "temperature": 0.3,
            "top_p": 0.9
        }

        try:
            async with session.post(self.url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content'].strip()
                else:
                    print(f"Error: {response.status}")
                    return ""
        except Exception as e:
            print(f"Error in translation: {e}")
            return ""

    async def translate(self, texts, original_lang, target_lang):
        """异步批量翻译"""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.translate_single(session, text, original_lang, target_lang)
                for text in texts
            ]
            return await asyncio.gather(*tasks)
class Doubao_translation:
    def __init__(self):
        config = load_config.load_config()
        self.api_key = config['translation_services']['Doubao']['auth_key']
        self.url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.model = config['translation_services']['Doubao']['model_name']

    async def translate_single(self, session, text, original_lang, target_lang):
        """单个文本的异步翻译"""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": f"Translate from {original_lang} to {target_lang}. Return ONLY the translation. No explanations. No notes. No annotations."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "temperature": 0.3,
            "top_p": 0.9
        }

        try:
            async with session.post(self.url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content'].strip()
                else:
                    print(f"Error: {response.status}")
                    return ""
        except Exception as e:
            print(f"Error in translation: {e}")
            return ""

    async def translate(self, texts, original_lang, target_lang):
        """异步批量翻译"""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.translate_single(session, text, original_lang, target_lang)
                for text in texts
            ]
            return await asyncio.gather(*tasks)
class Qwen_translation:
    def __init__(self):
        config = load_config.load_config()
        self.api_key = config['translation_services']['Qwen']['auth_key']
        self.url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.model = config['translation_services']['Qwen']['model_name']

    async def translate_single(self, session, text, original_lang, target_lang):
        """单个文本的异步翻译"""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": f"You are a professional translator. Translate from {original_lang} to {target_lang}.Return only the translations"
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "temperature": 0.3,
            "top_p": 0.9
        }

        try:
            async with session.post(self.url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content'].strip()
                else:
                    print(f"Error: {response.status}")
                    return ""
        except Exception as e:
            print(f"Error in translation: {e}")
            return ""

    async def translate(self, texts, original_lang, target_lang):
        """异步批量翻译"""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.translate_single(session, text, original_lang, target_lang)
                for text in texts
            ]
            return await asyncio.gather(*tasks)



# 测试代码
async def main():
    texts = [
        "Hello, how are you?",
        "What's the weather like today?",
        "I love programming",
        "Python is awesome",
        "Machine learning is interesting"
    ]

    # OpenAI翻译测试
    openai_translator = Openai_translation("gpt-3.5-turbo")
    translated_openai = await openai_translator.translate(
        texts=texts,
        original_lang="en",
        target_lang="zh"
    )
    print("OpenAI translations:")
    for src, tgt in zip(texts, translated_openai):
        print(f"{src} -> {tgt}")

    # DeepSeek翻译测试
    deepseek_translator = Deepseek_translation()
    translated_deepseek = await deepseek_translator.translate(
        texts=texts,
        original_lang="en",
        target_lang="zh"
    )
    print("\nDeepSeek translations:")
    for src, tgt in zip(texts, translated_deepseek):
        print(f"{src} -> {tgt}")

    qwen_translator = Qwen_translation()
    translated_deepseek = await qwen_translator.translate(
        texts=texts,
        original_lang="en",
        target_lang="zh"
    )
    print("\nQwen translations:")
    for src, tgt in zip(texts, translated_deepseek):
        print(f"{src} -> {tgt}")

if __name__ == "__main__":
    asyncio.run(main())
