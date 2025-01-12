from alibabacloud_alimt20181012.client import Client as alimt20181012Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alimt20181012 import models as alimt_20181012_models
from alibabacloud_tea_util import models as util_models
import load_config
import json

load_config = load_config.load_config()
credentials = load_config['translation_services']['alicloud']


class Sample:
    def __init__(self, source_text, original_lang, target_lang):
        self.source_text = source_text
        self.original_lang = original_lang or 'zh'
        self.target_lang = target_lang or 'en'

    @staticmethod
    def create_client() -> alimt20181012Client:
        config = open_api_models.Config(
            access_key_id=credentials["access_key_id"],
            access_key_secret=credentials["access_key_secret"]
        )
        config.endpoint = 'mt.cn-hangzhou.aliyuncs.com'
        return alimt20181012Client(config)

    def main(self):
        client = Sample.create_client()
        try:
            # 将输入转换为JSON格式
            if isinstance(self.source_text, str):
                source_text_json = json.dumps({"text": self.source_text})
            else:
                source_text_json = json.dumps(self.source_text)

            translate_request = alimt_20181012_models.TranslateGeneralRequest(
                source_language=self.original_lang,
                target_language=self.target_lang,
                source_text=source_text_json,
                scene="general",
                format_type="text"
            )
            runtime = util_models.RuntimeOptions()
            response = client.translate_general_with_options(translate_request, runtime)

            if not response or not response.body or not response.body.data:
                print("翻译响应为空")
                return None

            translated_text = response.body.data.translated
            print(f"API返回的原始翻译结果: {translated_text}")  # 添加调试输出

            # 尝试解析返回的JSON结果
            try:
                if isinstance(self.source_text, str):
                    # 单个文本的情况
                    translated_json = json.loads(translated_text)
                    return translated_json.get("text", translated_text)
                else:
                    # 多个文本的情况
                    try:
                        translated_json = json.loads(translated_text)
                        return translated_json
                    except json.JSONDecodeError:
                        # 如果不是JSON格式，按换行符分割
                        return translated_text.split('\n')
            except json.JSONDecodeError:
                return translated_text

        except Exception as e:
            print(f"翻译过程错误: {str(e)}")
            return None


def translate(texts, original_lang=None, target_lang=None):
    if not texts:
        return None

    if isinstance(texts, str):
        # 单个字符串翻译
        sample = Sample(texts, original_lang or 'zh', target_lang or 'en')
        return sample.main()
    else:
        # 多个文本翻译
        text_dict = {str(i + 1): text for i, text in enumerate(texts)}
        sample = Sample(text_dict, original_lang or 'zh', target_lang or 'en')
        result = sample.main()

        # 添加调试输出
        print(f"多个文本翻译的结果类型: {type(result)}")
        print(f"多个文本翻译的结果内容: {result}")

        if isinstance(result, dict):
            # 如果结果是字典，按序号提取
            return [result.get(str(i + 1)) for i in range(len(texts))]
        elif isinstance(result, list):
            # 如果结果是列表，直接返回
            return result
        elif isinstance(result, str):
            # 如果结果是字符串，按换行符分割
            return result.split('\n')
        return None


if __name__ == '__main__':
    # 测试用例
    # 单个文本测试
    single_text = "你好世界"
    single_result = translate(single_text)
    print("单个文本翻译结果:", single_result)

    # 多个文本测试
    test_texts = ['你好男孩', "回家去吧", "我们可以战胜他们"]
    result = translate(texts=test_texts, original_lang='zh', target_lang='en')
    print("多个文本翻译结果:", result)
