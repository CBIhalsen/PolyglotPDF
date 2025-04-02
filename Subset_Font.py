from fontTools.subset import Subsetter, Options
from fontTools.ttLib import TTFont
import datetime
import os
import requests


def download_font_from_github(language, font_filename, target_path):
    """
    从GitHub下载字体文件
    """

    # 构建GitHub原始文件URL
    github_base_url = "https://raw.githubusercontent.com/CBIhalsen/PolyglotPDF-fonts/main"
    font_folder = f"{language}_fonts"
    github_url = f"{github_base_url}/{font_folder}/{font_filename}"

    try:
        # 下载文件
        response = requests.get(github_url)

        # 检查是否存在（GitHub返回404表示文件不存在）
        if response.status_code == 404:
            print("\n=== 字体文件未找到 ===")
            print(f"在GitHub仓库中未找到所需的字体文件:")
            print(f"- 语言: {language}")
            print(f"- 字体文件: {font_filename}")
            print(f"- 预期路径: {font_folder}/{font_filename}")
            print("\n请通过以下步骤请求添加字体：")
            print("1. 访问: https://github.com/CBIhalsen/PolyglotPDF-fonts")
            print("2. 创建新的Issue")
            print("3. 标题: [Font Request] Add font for {language}")
            print("4. 内容:")
            print(f"   - Language: {language}")
            print(f"   - Font filename: {font_filename}")
            print(f"   - Expected path: {font_folder}/{font_filename}")
            print("   - Additional details: (请描述使用场景和需求)\n")
            return False

        response.raise_for_status()  # 检查其他可能的错误

        # 创建目标文件夹并保存文件
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, 'wb') as f:
            f.write(response.content)

        print(f"成功从GitHub下载字体文件到: {target_path}")
        return True

    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.ConnectionError):
            print(f"网络连接错误: 无法连接到GitHub。请检查您的网络连接。")
        elif isinstance(e, requests.exceptions.Timeout):
            print(f"请求超时: GitHub响应时间过长。")
        else:
            print(f"下载字体文件失败: {str(e)}")
        return False


def check_glyph_coverage(font, text):
    """
    检查字体是否包含所需的所有字形
    返回未找到的字符列表
    """
    cmap = font.getBestCmap()
    missing_chars = []

    for char in text:
        if ord(char) not in cmap:
            missing_chars.append(char)

    return missing_chars


def subset_font(in_font_path, out_font_path, text, language):
    b = datetime.datetime.now()
    """
    使用 fontTools 对 in_font_path 做子集化，
    只保留 text 中出现的字符，输出到 out_font_path。
    """

    # 检查输入字体文件是否存在
    if not os.path.exists(in_font_path):
        print(f"输入字体文件不存在: {in_font_path}")
        print("尝试从GitHub下载字体文件...")

        # 获取原始字体文件名
        font_filename = os.path.basename(in_font_path)

        # 尝试下载字体
        if not download_font_from_github(language, font_filename, in_font_path):
            print("无法获取字体文件，子集化操作终止")
            return

    # 确保输出文件夹存在
    output_dir = os.path.dirname(out_font_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录: {output_dir}")

    # 去重并排序要保留的字符
    unique_chars = "".join(sorted(set(text)))

    # 读取原字体
    font = TTFont(in_font_path)

    # 检查字形覆盖
    missing_chars = check_glyph_coverage(font, unique_chars)
    if missing_chars:
        print("\n=== 字形缺失警告 ===")
        print(f"字体文件 {os.path.basename(in_font_path)} 中未找到以下字符:")
        print("".join(missing_chars))
        print("这些字符将使用 PyMuPDF 默认字体进行显示")
        print("==================\n")

        # 从text中移除缺失的字符,只对有字形的字符进行子集化
        for char in missing_chars:
            unique_chars = unique_chars.replace(char, '')

    # 配置子集化选项
    options = Options()

    # 创建子集器并指定要包含的字符
    subsetter = Subsetter(options=options)
    subsetter.populate(text=unique_chars)

    # 对字体做子集化
    subsetter.subset(font)

    # 保存子集化后的 TTF
    font.save(out_font_path)
    print(f"生成子集字体: {out_font_path} (仅包含所需字形)")

    e = datetime.datetime.now()
    elapsed_time = (e - b).total_seconds()
    print(f"子集化运行时间: {elapsed_time} 秒")
