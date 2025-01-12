from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tmt.v20180321 import tmt_client, models
import json
import load_config

def translate(source_text_list,original_lang,target_lang):
    # 实例化一个认证对象
    config = load_config.load_config()

    credentials = config['translation_services']['tencent']
    cred = credential.Credential(credentials['SecretId'], credentials['SecretKey'])

    # 实例化一个http选项
    httpProfile = HttpProfile()
    httpProfile.endpoint = "tmt.tencentcloudapi.com"

    # 实例化一个client选项
    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile

    # 实例化要请求产品的client对象
    client = tmt_client.TmtClient(cred, "eu-frankfurt", clientProfile)

    # 实例化一个请求对象
    req = models.TextTranslateBatchRequest()

    # 填充请求参数
    req.Source = original_lang
    req.Target = target_lang
    req.ProjectId = 0
    req.SourceTextList = source_text_list

    # 发起请求并处理响应
    resp = client.TextTranslateBatch(req)

    # 解析响应并提取翻译结果
    response_dict = json.loads(resp.to_json_string())
    return response_dict['TargetTextList']


# 测试代码
if __name__ == "__main__":
    test_texts = ["how are you", "Today is a good day.222"]
    translated_texts = translate(test_texts,'zh')
    print(translated_texts)
