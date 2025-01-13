import requests
import os


support_language = [
    "en",  # 英语 English
    "zh",  # 中文 Chinese
    "es",  # 西班牙语 Spanish
    "fr",  # 法语 French
    "de",  # 德语 German
    "ru",  # 俄语 Russian
    "ar",  # 阿拉伯语 Arabic
    "it",  # 意大利语 Italian
    "ja",  # 日语 Japanese
    "ko",  # 韩语 Korean
    "nl",  # 荷兰语 Dutch
    "pt",  # 葡萄牙语 Portuguese
    "tr",  # 土耳其语 Turkish
    "sv",  # 瑞典语 Swedish
    "pl",  # 波兰语 Polish
    "fi",  # 芬兰语 Finnish
    "da",  # 丹麦语 Danish
    "no",  # 挪威语 Norwegian
    "cs",  # 捷克语 Czech
    "el",  # 希腊语 Greek
    "hu",  # 匈牙利语 Hungarian
    "th"   # 泰语 Thai
]

def download_file(url, dest_folder, file_name):
    """
    下载文件并保存到指定的文件夹中。
    """
    response = requests.get(url, allow_redirects=True)
    if response.status_code == 200:
        with open(os.path.join(dest_folder, file_name), 'wb') as file:
            file.write(response.content)
    else:
        print(f"Failed to download {file_name}. Status code: {response.status_code}")

def download_model_files(model_name):
    """
    根据模型名称下载模型文件。
    """
    # 文件列表
    files_to_download = [
        "config.json",
        "pytorch_model.bin",
        "tokenizer_config.json",
        "vocab.json",
        "source.spm",
        "target.spm"  # 如果模型不使用SentencePiece，这两个文件可能不需要
    ]

    # 创建模型文件夹
    # 创建模型文件夹
    model_folder_name = model_name.split('/')[-1]  # 从模型名称中获取文件夹名称
    model_folder = os.path.join("translation_models", model_folder_name)  # 添加相对路径前缀

    if os.path.exists(model_folder):
        return


    if not os.path.exists(model_folder):
        os.makedirs(model_folder)

    # 构建下载链接并下载文件
    base_url = f"https://huggingface.co/{model_name}/resolve/main/"
    for file_name in files_to_download:
        download_url = base_url + file_name
        print(f"Downloading {file_name}...")
        download_file(download_url, model_folder, file_name)

# 示例使用
if __name__ == '__main__':

    model_name = "Helsinki-NLP/opus-mt-en-es"
    download_model_files(model_name)

