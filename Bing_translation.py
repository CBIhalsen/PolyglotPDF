import re
import requests
import time
import threading
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

def translate(texts, original_lang, target_lang):
    """
    使用Bing翻译API翻译文本列表 - 高性能实现
    
    Args:
        texts: 要翻译的文本列表
        original_lang: 源语言代码
        target_lang: 目标语言代码
        
    Returns:
        翻译后的文本列表
    """
    # 确保输入文本为列表格式
    if isinstance(texts, str):
        texts = [texts]
    
    # 如果文本量小，使用简单的并发线程池
    if len(texts) <= 20:
        return translate_with_threadpool(texts, original_lang, target_lang)
    
    # 对于大量文本，使用异步IO处理
    return translate_with_asyncio(texts, original_lang, target_lang)


def translate_with_threadpool(texts, original_lang, target_lang, max_workers=5):
    """使用线程池并发翻译小批量文本"""
    translator = BingTranslator(lang_in=original_lang, lang_out=target_lang)
    translated_texts = [""] * len(texts)
    
    def translate_one(index, text):
        try:
            translated_texts[index] = translator.do_translate(text)
        except Exception as e:
            print(f"翻译文本时出错 (索引 {index}): {e}")
            translated_texts[index] = ""
    
    # 使用线程池并发处理
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(translate_one, i, text) 
                  for i, text in enumerate(texts)]
        
        # 等待所有任务完成
        for future in futures:
            future.result()
    
    return translated_texts


def translate_with_asyncio(texts, original_lang, target_lang):
    """使用asyncio异步处理大批量文本"""
    # 定义异步主函数
    async def main():
        translator = AsyncBingTranslator(lang_in=original_lang, lang_out=target_lang)
        return await translator.translate_batch(texts)
    
    # 如果当前线程没有事件循环，创建一个新的
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # 运行异步函数并返回结果
    return loop.run_until_complete(main())


def split_text_intelligently(text, max_length=1000):
    """智能分段文本，尽量在句子边界处断开"""
    if len(text) <= max_length:
        return [text]
        
    parts = []
    start = 0
    
    while start < len(text):
        # 如果剩余文本不足max_length，直接添加
        if len(text) - start <= max_length:
            parts.append(text[start:])
            break
            
        # 计算当前段落的结束位置
        end = start + max_length
        
        # 尝试在句子结束处断开（优先级：段落 > 句号 > 逗号 > 空格）
        paragraph_break = text.rfind('\n', start, end)
        if paragraph_break != -1 and paragraph_break > start + max_length * 0.5:
            end = paragraph_break + 1
        else:
            # 寻找句号、问号、感叹号等
            for sep in ['. ', '。', '？', '！', '? ', '! ']:
                pos = text.rfind(sep, start, end)
                if pos != -1 and pos > start + max_length * 0.5:
                    end = pos + len(sep)
                    break
            else:
                # 如果没找到句号，尝试在逗号处断开
                for sep in [', ', '，', '; ', '；']:
                    pos = text.rfind(sep, start, end)
                    if pos != -1 and pos > start + max_length * 0.7:
                        end = pos + len(sep)
                        break
                else:
                    # 实在没有好的断点就在空格处断开
                    pos = text.rfind(' ', start + max_length * 0.8, end)
                    if pos != -1:
                        end = pos + 1
        
        parts.append(text[start:end])
        start = end
    
    return parts


class BingTranslator:
    name = "bing"
    lang_map = {"zh": "zh-Hans"}
    
    # 会话参数缓存
    _cache_lock = threading.Lock()
    _sid_cache = None
    _sid_timestamp = 0
    _sid_cache_ttl = 300  # 5分钟缓存有效期

    def __init__(self, lang_in, lang_out, model=None, ignore_cache=False):
        # 处理语言代码映射
        self.lang_in = self.lang_map.get(lang_in, lang_in)
        self.lang_out = self.lang_map.get(lang_out, lang_out)
        
        # 自动语言检测处理
        if self.lang_in == "auto":
            self.lang_in = "auto-detect"
            
        self.model = model
        self.ignore_cache = ignore_cache
        self.session = requests.Session()
        self.endpoint = "https://www.bing.com/translator"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        }

    def find_sid(self):
        """获取必要的会话参数，使用缓存减少请求"""
        current_time = time.time()
        
        # 检查缓存是否有效
        with self._cache_lock:
            if (not self.ignore_cache and 
                BingTranslator._sid_cache is not None and 
                (current_time - BingTranslator._sid_timestamp) < BingTranslator._sid_cache_ttl):
                return BingTranslator._sid_cache
        
        # 缓存无效，重新获取参数
        response = self.session.get(self.endpoint, headers=self.headers)
        response.raise_for_status()
        url = response.url[:-10]
        ig = re.findall(r"\"ig\":\"(.*?)\"", response.text)[0]
        iid = re.findall(r"data-iid=\"(.*?)\"", response.text)[-1]
        key, token = re.findall(
            r"params_AbusePreventionHelper\s=\s\[(.*?),\"(.*?)\",", response.text
        )[0]
        
        # 更新缓存
        result = (url, ig, iid, key, token)
        with self._cache_lock:
            BingTranslator._sid_cache = result
            BingTranslator._sid_timestamp = current_time
        
        return result

    def do_translate(self, text):
        """执行翻译"""
        if not text or not text.strip():
            return ""
            
        # 如果文本超过1000字符，分段翻译
        if len(text) > 1000:
            parts = split_text_intelligently(text)
            translated_parts = []
            
            for part in parts:
                url, ig, iid, key, token = self.find_sid()
                response = self.session.post(
                    f"{url}ttranslatev3?IG={ig}&IID={iid}",
                    data={
                        "fromLang": self.lang_in,
                        "to": self.lang_out,
                        "text": part[:1000],  # 确保不超过1000
                        "token": token,
                        "key": key,
                    },
                    headers=self.headers,
                )
                response.raise_for_status()
                translated_parts.append(response.json()[0]["translations"][0]["text"])
                
            return ''.join(translated_parts)
        
        url, ig, iid, key, token = self.find_sid()
        response = self.session.post(
            f"{url}ttranslatev3?IG={ig}&IID={iid}",
            data={
                "fromLang": self.lang_in,
                "to": self.lang_out,
                "text": text,
                "token": token,
                "key": key,
            },
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()[0]["translations"][0]["text"]


class AsyncBingTranslator:
    """异步Bing翻译器实现"""
    lang_map = {"zh": "zh-Hans"}
    
    # 会话参数缓存
    _sid_cache = None
    _sid_timestamp = 0
    _sid_cache_ttl = 300  # 5分钟缓存有效期

    def __init__(self, lang_in, lang_out):
        self.lang_in = self.lang_map.get(lang_in, lang_in)
        self.lang_out = self.lang_map.get(lang_out, lang_out)
        
        if self.lang_in == "auto":
            self.lang_in = "auto-detect"
            
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        }
        self.endpoint = "https://www.bing.com/translator"

    async def find_sid(self, session):
        """异步获取会话参数，带缓存"""
        current_time = time.time()
        
        # 检查缓存是否有效
        if (AsyncBingTranslator._sid_cache is not None and 
            (current_time - AsyncBingTranslator._sid_timestamp) < AsyncBingTranslator._sid_cache_ttl):
            return AsyncBingTranslator._sid_cache
        
        # 缓存无效，异步获取新参数
        async with session.get(self.endpoint, headers=self.headers) as response:
            if response.status != 200:
                raise Exception(f"获取会话参数失败: HTTP {response.status}")
                
            text = await response.text()
            url = str(response.url)[:-10]
            ig = re.findall(r"\"ig\":\"(.*?)\"", text)[0]
            iid = re.findall(r"data-iid=\"(.*?)\"", text)[-1]
            key, token = re.findall(
                r"params_AbusePreventionHelper\s=\s\[(.*?),\"(.*?)\",", text
            )[0]
            
            # 更新缓存
            result = (url, ig, iid, key, token)
            AsyncBingTranslator._sid_cache = result
            AsyncBingTranslator._sid_timestamp = current_time
            
            return result

    async def translate_text(self, session, text):
        """翻译单个文本"""
        if not text or not text.strip():
            return ""
        
        # 如果文本超过1000字符，分段翻译
        if len(text) > 1000:
            parts = split_text_intelligently(text)
            translated_parts = []
            
            # 非递归异步处理每个文本块
            for part in parts:
                url, ig, iid, key, token = await self.find_sid(session)
                
                async with session.post(
                    f"{url}ttranslatev3?IG={ig}&IID={iid}",
                    data={
                        "fromLang": self.lang_in,
                        "to": self.lang_out,
                        "text": part[:1000],  # 确保不超过1000
                        "token": token,
                        "key": key,
                    },
                    headers=self.headers,
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        translated_parts.append(result[0]["translations"][0]["text"])
                    else:
                        print(f"翻译请求失败: HTTP {response.status}")
                        translated_parts.append("")
            
            return ''.join(translated_parts)
        
        try:
            url, ig, iid, key, token = await self.find_sid(session)
            response = await session.post(
                f"{url}ttranslatev3?IG={ig}&IID={iid}",
                data={
                    "fromLang": self.lang_in,
                    "to": self.lang_out,
                    "text": text,
                    "token": token,
                    "key": key,
                },
                headers=self.headers,
            )
            if response.status == 200:
                result = await response.json()
                return result[0]["translations"][0]["text"]
            else:
                print(f"翻译请求失败: HTTP {response.status}")
                return ""
        except Exception as e:
            print(f"翻译过程中发生错误: {e}")
            print(f"原文: {text}")
            return ""

    async def translate_batch(self, texts, batch_size=10, max_concurrent=5):
        """批量翻译文本，控制并发数量和请求批次"""
        async with aiohttp.ClientSession() as session:
            results = [""] * len(texts)
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def translate_with_limit(index, text):
                retry_count = 0
                max_retries = 10
                backoff_time = 1.0  # 初始重试等待时间
                
                while retry_count < max_retries:
                    try:
                        async with semaphore:
                            # 每批次间隔较小的延迟
                            if index > 0 and index % batch_size == 0:
                                await asyncio.sleep(0.1)
                            

                            translated = await self.translate_text(session, text)
                            if translated:  # 如果翻译成功
                                results[index] = translated
                                if retry_count > 0:  # 如果是重试成功的
                                    print(f"第{index}个文本重试成功！")
                                return
                    except Exception as e:
                        print(f"第{index}个文本翻译失败 (尝试 {retry_count+1}/{max_retries}): {e}")
                        print(f"原文: {text}")
                    
                    # 如果到这里，说明需要重试
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"将在{backoff_time}秒后重试...")
                        await asyncio.sleep(backoff_time)
                        backoff_time *= 2  # 指数退避策略
                    else:
                        print(f"已达到最大重试次数，翻译失败")
                        results[index] = ""
            
            # 创建所有任务
            tasks = [
                asyncio.create_task(translate_with_limit(i, text))
                for i, text in enumerate(texts)
            ]
            
            # 等待所有任务完成
            await asyncio.gather(*tasks)
            return results


# 测试代码
if __name__ == "__main__":
    test_texts = ["Hello, world!", "How are you today?", "Python is amazing", "I love programming"]
    results = translate(test_texts, "en", "zh")
    
    for original, translated in zip(test_texts, results):
        print(f"Original: {original}")
        print(f"Translated: {translated}")
        print("-" * 30)