

text = "今日は（こんにちは）"

# 方法2：直接使用detect
from langdetect import detect
lang_code = detect(text)
print(lang_code)  # 输出: ja
