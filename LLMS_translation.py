import asyncio
import aiohttp
import re
import requests

import load_config

class AI302_translation:
    def __init__(self):
        config = load_config.load_config()
        self.api_key = config['translation_services']['AI302']['auth_key']
        self.url = "https://api.302.ai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.model = config['translation_services']['AI302']['model_name']
        # 从配置中读取翻译提示词
        self.prompt_template = config.get('translation_prompt', {}).get('system_prompt', 
            'You are a professional translator. Translate from {original_lang} to {target_lang}. Return only the translation without explanations or notes.')

    async def translate_single(self, session, text, original_lang, target_lang):
        """单个文本的异步翻译"""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self.prompt_template.format(original_lang=original_lang, target_lang=target_lang)
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
        print(f"Starting 302.ai translation of {len(texts)} texts")
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.translate_single(session, text, original_lang, target_lang)
                for text in texts
            ]
            results = await asyncio.gather(*tasks)
            print(f"302.ai translation completed, {len(results)} texts translated")
            return results

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
        # 从配置中读取翻译提示词
        self.prompt_template = config.get('translation_prompt', {}).get('system_prompt', 
            'You are a professional translator. Translate from {original_lang} to {target_lang}. Return only the translation without explanations or notes.')

    async def translate_single(self, session, text, original_lang, target_lang):
        """单个文本的异步翻译"""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self.prompt_template.format(original_lang=original_lang, target_lang=target_lang)
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

# 添加Bing翻译类
class Bing_translation:
    def __init__(self):
        self.session = requests.Session()
        self.endpoint = "https://www.bing.com/translator"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        }
        self.lang_map = {"zh": "zh-Hans"}

    async def find_sid(self):
        """获取必要的会话参数"""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: self.session.get(self.endpoint, headers=self.headers))
        response.raise_for_status()
        url = response.url[:-10]
        ig = re.findall(r"\"ig\":\"(.*?)\"", response.text)[0]
        iid = re.findall(r"data-iid=\"(.*?)\"", response.text)[-1]
        key, token = re.findall(
            r"params_AbusePreventionHelper\s=\s\[(.*?),\"(.*?)\",", response.text
        )[0]
        return url, ig, iid, key, token

    async def translate_single(self, session, text, original_lang, target_lang):
        """单个文本的异步翻译"""
        if not text or not text.strip():
            return ""
            
        # 处理语言代码映射
        lang_in = self.lang_map.get(original_lang, original_lang)
        lang_out = self.lang_map.get(target_lang, target_lang)
        
        # 自动语言检测处理
        if lang_in == "auto":
            lang_in = "auto-detect"
        
        # Bing翻译最大长度限制
        text = text[:1000]
        
        try:
            url, ig, iid, key, token = await self.find_sid()
            
            # 通过异步HTTP请求执行翻译
            async with session.post(
                f"{url}ttranslatev3?IG={ig}&IID={iid}",
                data={
                    "fromLang": lang_in,
                    "to": lang_out,
                    "text": text,
                    "token": token,
                    "key": key,
                },
                headers=self.headers,
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result[0]["translations"][0]["text"]
                else:
                    error_text = await response.text()
                    print(f"Bing翻译错误: {response.status}, 详情: {error_text}")
                    return ""
        except Exception as e:
            print(f"Bing翻译过程中发生错误: {e}")
            return ""

    async def translate(self, texts, original_lang, target_lang):
        """异步批量翻译"""
        print(f"开始Bing翻译，共 {len(texts)} 个文本")
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i, text in enumerate(texts):
                # 添加延迟以避免请求过快被屏蔽
                await asyncio.sleep(0.5 * (i % 3))  # 每3个请求一组，每组之间间隔0.5秒
                tasks.append(self.translate_single(session, text, original_lang, target_lang))
            
            results = await asyncio.gather(*tasks)
            print(f"Bing翻译完成，共翻译 {len(results)} 个文本")
            return results

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
        # 从配置中读取翻译提示词
        self.prompt_template = config.get('translation_prompt', {}).get('system_prompt', 
            'You are a professional translator. Translate from {original_lang} to {target_lang}. Return only the translation without explanations or notes.')

    async def translate_single(self, session, text, original_lang, target_lang):
        """单个文本的异步翻译"""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self.prompt_template.format(original_lang=original_lang, target_lang=target_lang)
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
        # 从配置中读取翻译提示词
        self.prompt_template = config.get('translation_prompt', {}).get('system_prompt', 
            'You are a professional translator. Translate from {original_lang} to {target_lang}. Return only the translation without explanations or notes.')

    async def translate_single(self, session, text, original_lang, target_lang):
        """单个文本的异步翻译"""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self.prompt_template.format(original_lang=original_lang, target_lang=target_lang)
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
        # 从配置中读取翻译提示词
        self.prompt_template = config.get('translation_prompt', {}).get('system_prompt', 
            'You are a professional translator. Translate from {original_lang} to {target_lang}. Return only the translation without explanations or notes.')

    async def translate_single(self, session, text, original_lang, target_lang):
        """单个文本的异步翻译"""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self.prompt_template.format(original_lang=original_lang, target_lang=target_lang)
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

class Grok_translation:
    def __init__(self):
        config = load_config.load_config()
        # 修改键名为大写的'Grok'以匹配其他API命名风格
        self.api_key = config['translation_services']['Grok']['auth_key']
        self.url = "https://api-proxy.me/xai/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
            "Authorization": f"Bearer {self.api_key}"
        }
        self.model = config['translation_services']['Grok']['model_name']
        # 从配置中读取翻译提示词
        self.prompt_template = config.get('translation_prompt', {}).get('system_prompt', 
            'You are a professional translator. Translate from {original_lang} to {target_lang}. Return only the translation without explanations or notes.')

    async def translate_single(self, session, text, original_lang, target_lang):
        """单个文本的异步翻译"""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self.prompt_template.format(original_lang=original_lang, target_lang=target_lang)
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "temperature": 0.3,
            "stream": False
        }

        try:
            async with session.post(self.url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    translated_text = result['choices'][0]['message']['content'].strip()
                    # 添加调试日志
                    #print(f"Grok translated: '{text[:30]}...' -> '{translated_text[:30]}...'")
                    return translated_text
                else:
                    error_text = await response.text()
                    print(f"Error: {response.status}, Details: {error_text}")
                    return ""
        except Exception as e:
            print(f"Error in translation: {e}")
            return ""

    async def translate(self, texts, original_lang, target_lang):
        """异步批量翻译"""
        print(f"Starting Grok translation of {len(texts)} texts")
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.translate_single(session, text, original_lang, target_lang)
                for text in texts
            ]
            results = await asyncio.gather(*tasks)
            print(f"Grok translation completed, {len(results)} texts translated")
            return results

class ThirdParty_translation:
    def __init__(self):
        config = load_config.load_config()
        self.api_key = config['translation_services']['ThirdParty']['auth_key']
        self.url = config['translation_services']['ThirdParty']['api_url']
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.model = config['translation_services']['ThirdParty']['model_name']
        # 从配置中读取翻译提示词
        self.prompt_template = config.get('translation_prompt', {}).get('system_prompt', 
            'You are a professional translator. Translate from {original_lang} to {target_lang}. Return only the translation without explanations or notes.')

    async def translate_single(self, session, text, original_lang, target_lang):
        """单个文本的异步翻译"""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self.prompt_template.format(original_lang=original_lang, target_lang=target_lang)
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "temperature": 0.3,
            "stream": False
        }

        try:
            async with session.post(self.url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    translated_text = result['choices'][0]['message']['content'].strip()
                    # 添加调试日志
                    #print(f"ThirdParty translated: '{text[:30]}...' -> '{translated_text[:30]}...'")
                    return translated_text
                else:
                    error_text = await response.text()
                    print(f"Error: {response.status}, Details: {error_text}")
                    return ""
        except Exception as e:
            print(f"Error in translation: {e}")
            return ""

    async def translate(self, texts, original_lang, target_lang):
        """异步批量翻译"""
        print(f"Starting ThirdParty translation of {len(texts)} texts")
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.translate_single(session, text, original_lang, target_lang)
                for text in texts
            ]
            results = await asyncio.gather(*tasks)
            print(f"ThirdParty translation completed, {len(results)} texts translated")
            return results

class GLM_translation:
    def __init__(self):
        config = load_config.load_config()
        self.api_key = config['translation_services']['GLM']['auth_key']
        self.url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.model = config['translation_services']['GLM']['model_name']
        # 从配置中读取翻译提示词
        self.prompt_template = config.get('translation_prompt', {}).get('system_prompt', 
            'You are a professional translator. Translate from {original_lang} to {target_lang}. Return only the translation without explanations or notes.')

    async def translate_single(self, session, text, original_lang, target_lang):
        """单个文本的异步翻译"""
        # 过滤控制字符，解决GLM 1213错误
        cleaned_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        if not cleaned_text.strip():
            return ""
            
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self.prompt_template.format(original_lang=original_lang, target_lang=target_lang)
                },
                {
                    "role": "user",
                    "content": cleaned_text
                }
            ],
            "temperature": 0.3,
            "top_p": 0.7,
            "do_sample": False
        }

        try:
            async with session.post(self.url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content'].strip()
                else:
                    error_text = await response.text()
                    print(f"Error: {response.status}, Details: {error_text}")
                    return ""
        except Exception as e:
            print(f"Error in GLM translation: {e}")
            return ""

    async def translate(self, texts, original_lang, target_lang):
        """异步批量翻译"""
        print(f"Starting GLM translation of {len(texts)} texts")
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.translate_single(session, text, original_lang, target_lang)
                for text in texts
            ]
            results = await asyncio.gather(*tasks)
            print(f"GLM translation completed, {len(results)} texts translated")
            return results

# 测试代码
async def main():
    texts = [
        "Hello, how are you?",
        "What's the weather like today?",
        "I love programming",
        "Python is awesome",
        "Machine learning is interesting"
    ]

    # 302.ai翻译测试
    ai302_translator = AI302_translation()
    translated_ai302 = await ai302_translator.translate(
        texts=texts,
        original_lang="en",
        target_lang="zh"
    )
    print("302.ai translations:")
    for src, tgt in zip(texts, translated_ai302):
        print(f"{src} -> {tgt}")

    # OpenAI翻译测试
    openai_translator = Openai_translation()
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

    # Grok翻译测试
    grok_translator = Grok_translation()
    translated_grok = await grok_translator.translate(
        texts=texts,
        original_lang="en",
        target_lang="zh"
    )
    print("\nGrok translations:")
    for src, tgt in zip(texts, translated_grok):
        print(f"{src} -> {tgt}")

    # 添加ThirdParty翻译测试
    try:
        thirdparty_translator = ThirdParty_translation()
        translated_thirdparty = await thirdparty_translator.translate(
            texts=texts,
            original_lang="en",
            target_lang="zh"
        )
        print("\nThirdParty translations:")
        for src, tgt in zip(texts, translated_thirdparty):
            print(f"{src} -> {tgt}")
    except Exception as e:
        print(f"Error testing ThirdParty translation: {e}")

    # 添加 GLM 翻译测试
    try:
        glm_translator = GLM_translation()
        translated_glm = await glm_translator.translate(
            texts=texts,
            original_lang="en",
            target_lang="zh"
        )
        print("\nGLM translations:")
        for src, tgt in zip(texts, translated_glm):
            print(f"{src} -> {tgt}")
    except Exception as e:
        print(f"Error testing GLM translation: {e}")

    # 添加Bing翻译测试
    try:
        bing_translator = Bing_translation()
        translated_bing = await bing_translator.translate(
            texts=texts,
            original_lang="en",
            target_lang="zh"
        )
        print("\nBing translations:")
        for src, tgt in zip(texts, translated_bing):
            print(f"{src} -> {tgt}")
    except Exception as e:
        print(f"Error testing Bing translation: {e}")

if __name__ == "__main__":
    asyncio.run(main())
