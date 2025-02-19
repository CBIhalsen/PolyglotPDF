
import All_Translation as at
from PIL import Image
import pytesseract
import time
import fitz
import os
import download_model
import load_config
import re
from datetime import datetime
import pdf_thumbnail

config = load_config.load_config()
translation_type = config['default_services']['Translation_api']
translation = config['default_services']['Enable_translation']
use_mupdf = not config['default_services']['ocr_model']
# print(use_mupdf,'mupdf值')
# print('当前',config['count'])



def get_font_by_language(target_language):
    font_mapping = {
        'zh': "'Microsoft YaHei', 'SimSun'",  # 中文
        'en': "'Times New Roman', Arial",      # 英文
        'ja': "'MS Mincho', 'Yu Mincho'",     # 日文
        'ko': "'Malgun Gothic'",              # 韩文
    }
    # 如果找不到对应语言，返回默认字体
    return font_mapping.get(target_language, "'Times New Roman', Arial")


def is_math(text, page_num,font_info):
    """
    判断文本是否为非文本（如数学公式或者长度小于4的文本）
    """


    # 判断文本长度
    text_len = len(text)
    if text_len < 4:
        return True
    math_fonts = [
        # Computer Modern Math
        'CMMI', 'CMSY', 'CMEX',
        'CMMI5', 'CMMI6', 'CMMI7', 'CMMI8', 'CMMI9', 'CMMI10',
        'CMSY5', 'CMSY6', 'CMSY7', 'CMSY8', 'CMSY9', 'CMSY10',

        # AMS Math
        'MSAM', 'MSBM', 'EUFM', 'EUSM',

        # Times/Palatino Math
        'TXMI', 'TXSY', 'PXMI', 'PXSY',

        # Modern Math
        'CambriaMath', 'AsanaMath', 'STIXMath', 'XitsMath',
        'Latin Modern Math', 'Neo Euler'
    ]
    # 检查文本长度是否小于50且字体是否在数学字体列表中
    if text_len < 70 and any(math_font in font_info for math_font in math_fonts):
        return True

    if 15 < text_len <100:
        # 使用正则表达式找出所有5个或更多任意字符连续组成的单词
        long_words = re.findall(r'\S{5,}', text)
        if len(long_words) < 2:
            return True


    # 分行处理
    lines = text.split('\n')
    len_lines = len([line for line in lines if line.strip()])

    # 找到长度最小和最大的行
    min_line_len = min((len(line) for line in lines if line.strip()), default=text_len)
    max_line_len = max((len(line) for line in lines), default=text_len)

    # 计算空格比例
    newline_count = text.count('\n')
    total_spaces = text.count(' ') + (newline_count * 5)
    space_ratio = total_spaces / text_len if text_len > 0 else 0

    # 检查是否存在完整单词(5个或更多字符)
    text_no_spaces = text.replace(" ", "")
    has_complete_word = bool(re.search(r'.{5,}', text_no_spaces))

    # 如果没有完整单词,认为是非文本
    if not has_complete_word:

        return True

    # 计算数字占比
    digit_count = sum(c.isdigit() for c in text)
    digit_ratio = digit_count / text_len if text_len > 0 else 0

    # 如果数字占比超过30%，返回True
    if digit_ratio > 0.3:
        return True





    # 检查数学公式
    math_symbols = set("=∑θ∫∂√±ΣΠfδλσε∋∈µ→()|−ˆ,...")
    # 数学公式判断条件2:包含至少2个数学符号且总文本较短
    if sum(1 for sym in math_symbols if sym in text) >= 2 and len(text_no_spaces) < 25:
        return True

    # 数学公式判断条件1:包含至少2个数学符号且行短且行数少且最大行长度小
    if sum(1 for sym in math_symbols if sym in text) >= 2 and min_line_len < 10 and len_lines < 5 and max_line_len < 35:

        return True

    # 数学公式判断条件3:包含至少2个数学符号且空格比例高
    if sum(1 for sym in math_symbols if sym in text) >= 2 and space_ratio > 0.5:

        return True

    return False



def is_non_text(text):
    """
    判断是否为参考文献格式
    参数：
    text: 待检查的文本
    返回：
    bool: 如果是参考文献格式返回True，否则返回False
    """
    # 去除开头的空白字符
    text = text.lstrip()

    # 检查是否以[数字]开头
    pattern = r'^\[\d+\]'

    if re.match(pattern, text):
        return True

    return False
font_collection = []


class main_function:

    def __init__(self,original_language,target_language,pdf_path,index=0,DPI=150,):


        self.original_language = original_language
        self.target_language = target_language
        self.pdf_path = pdf_path
        self.full_path ='./static/original/' + pdf_path
        self.doc = fitz.open(self.full_path)
        self.DPI = DPI
        # self.pages = convert_from_path(self.full_path, DPI)  # 第二个参数是DPI（点每英寸）
        self.t = time.time()
        self.translation = translation
        self.translation_type = translation_type
        self.index = index+1


    def main(self,):
        # 直接调用函数执行
        load_config.update_count()
        config = load_config.load_config()
        count = config["count"]
        print("更新后", count)

        # 获取当前时间并格式化
        # print('kk')
        # print(self.full_path)
        pdf_thumbnail.create_pdf_thumbnail(self.full_path,width=400)
        # print(self.original_language,self.target_language,self.full_path,len(self.original_language),'路线信息')
        # pdf_thumbnail.create_pdf_thumbnail(self.full_path, width=400)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_entry = {
            "index": count,
            "date": current_time,
            "name": self.pdf_path,
            "original_language": self.original_language,
            "target_language": self.target_language,
            "read": "0",
            "statue": "0"
        }
        load_config.add_new_entry(new_entry)
    # 遍历每一页
        # 使用PyMuPDF直接获取文本块
        if use_mupdf:

            for i in range(self.doc.page_count):
                self.start(image=None, pag_num=i)
        else:
            zoom = self.DPI / 72  # 将 DPI 从默认的 72 调整到指定 DPI
            mat = fitz.Matrix(zoom, zoom)
            for i, page in enumerate(self.doc):
                pix = page.get_pixmap(matrix=mat)
                # 转换为 PIL Image 对象
                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                # 如果需要保存图像到文件
                # image.save(f'page_{i}.jpg', 'JPEG')
                self.start(image=image, pag_num=i)





    # 使用 os.path.splitext() 来分割路径和扩展名
        pdf_name, _ = os.path.splitext(self.pdf_path)
        self.doc.ez_save(f"./static/target/{pdf_name}_{self.target_language}.pdf", garbage=4, deflate=True)
        load_config.update_file_status(count, statue="1")# 更新index为2的条目的statue值为"1"
        # print(self.index)

        e = time.time()
        print(e - self.t)



    def start(self, image, pag_num):
        """
        处理单页PDF的函数
        Args:
            image: PDF页面的图像（用于OCR方式）
            pag_num: 页面编号
            use_mupdf: 是否使用PyMuPDF直接提取文本块（True）或使用OCR（False）
        """
        text_rect = []
        page = self.doc.load_page(pag_num)


        #
        if use_mupdf:
            # 使用PyMuPDF直接获取文本块
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                if block.get("type") == 0:  # 文本块
                    bbox = block["bbox"]
                    text = ""
                    font_info = None
                    # 收集文本和字体信息
                    # print(pag_num, '当前页面号')
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text += span["text"] + " "
                            font_size = span["size"]
                            # print(text)


                            # print("字体大小",font_size)
                            if not font_info and "font" in span:
                                font_info = span["font"]
                                # print('字体信息',font_info)
                                if font_info and font_info not in font_collection:
                                    font_collection.append(font_info)

                    text = text.strip()



                    # 只有不是公式的文本才添加到处理列表
                    if text and not is_math(text, pag_num,font_info) and  not is_non_text(text):
                        text_rect.append([text, bbox])

        else:
            # OCR方式
            Full_width, Full_height = image.size

            tesseract_path = config['ocr_services']['tesseract']['path']
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

            # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            ocr_result = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

            current_paragraph_text = ''
            current_block_num = 0
            last_block_left = 0
            last_block_right = 0
            last_block_height = 0
            paragraph_bbox = {'left': float('inf'), 'top': float('inf'), 'right': 0, 'bottom': 0}
            Threshold_width = 0.06 * Full_width
            Threshold_height = 0.006 * Full_height

            for i in range(len(ocr_result['text'])):
                block_num = ocr_result['block_num'][i]
                text = ocr_result['text'][i].strip()

                # 跳过公式
                if text and not is_math(text, pag_num,font_info='22') and  not is_non_text(text):
                    continue

                left = ocr_result['left'][i]
                top = ocr_result['top'][i]
                width = ocr_result['width'][i]
                height = ocr_result['height'][i]

                if block_num != current_block_num or (abs(left - last_block_right) > Threshold_width and
                                                      abs(height - last_block_height) > Threshold_height and
                                                      abs(left - last_block_left) > Threshold_width):

                    if current_paragraph_text != '':
                        x0_ratio = paragraph_bbox['left'] / Full_width
                        y0_ratio = paragraph_bbox['top'] / Full_height
                        x1_ratio = paragraph_bbox['right'] / Full_width
                        y1_ratio = paragraph_bbox['bottom'] / Full_height

                        Full_rect = page.rect
                        width_points = Full_rect.width
                        height_points = Full_rect.height

                        coordinates_ratio = (x0_ratio, y0_ratio, x1_ratio, y1_ratio)
                        x0_pdf = coordinates_ratio[0] * width_points
                        y0_pdf = coordinates_ratio[1] * height_points
                        x1_pdf = coordinates_ratio[2] * width_points
                        y1_pdf = coordinates_ratio[3] * height_points

                        text_rect.append([current_paragraph_text, (x0_pdf, y0_pdf, x1_pdf, y1_pdf)])

                        current_paragraph_text = ''
                        paragraph_bbox = {'left': float('inf'), 'top': float('inf'), 'right': 0, 'bottom': 0}

                    current_block_num = block_num

                if text:
                    current_paragraph_text += text + ' '
                    last_block_left = paragraph_bbox['left']

                    paragraph_bbox['left'] = min(paragraph_bbox['left'], left)
                    paragraph_bbox['top'] = min(paragraph_bbox['top'], top)
                    paragraph_bbox['right'] = max(paragraph_bbox['right'], left + width)
                    paragraph_bbox['bottom'] = max(paragraph_bbox['bottom'], top + height)
                    last_block_right = left + width
                    last_block_height = height

            # 处理最后一个段落
            if current_paragraph_text:
                x0_ratio = paragraph_bbox['left'] / Full_width
                y0_ratio = paragraph_bbox['top'] / Full_height
                x1_ratio = paragraph_bbox['right'] / Full_width
                y1_ratio = paragraph_bbox['bottom'] / Full_height

                Full_rect = page.rect
                width_points = Full_rect.width
                height_points = Full_rect.height

                coordinates_ratio = (x0_ratio, y0_ratio, x1_ratio, y1_ratio)
                x0_pdf = coordinates_ratio[0] * width_points
                y0_pdf = coordinates_ratio[1] * height_points
                x1_pdf = coordinates_ratio[2] * width_points
                y1_pdf = coordinates_ratio[3] * height_points

                text_rect.append([current_paragraph_text, (x0_pdf, y0_pdf, x1_pdf, y1_pdf)])

        # 处理翻译和文本插入
        first_strings = []
        texts_list = [item[0] for item in text_rect]



        if not texts_list:
            # print("Warning: No text found to translate!")
            return

        if self.translation and use_mupdf:
            # print(texts_list)
            translation_list = at.Online_translation(
                original_language=self.original_language,
                target_language=self.target_language,
                translation_type=self.translation_type,
                texts_to_process=texts_list
            ).translation()
        if self.translation and not use_mupdf:
            # print(texts_list)
            translation_list = at.Offline_translation(
                original_language=self.original_language,
                target_language=self.target_language,
                texts_to_process=texts_list
            ).translation()



        # 处理每个文本块
        for idx, item in enumerate(text_rect):
            first_strings.append(item[0])
            rect = fitz.Rect(item[1]) if use_mupdf else fitz.Rect(*item[1])

            try:
                page.add_redact_annot(rect)
                page.apply_redactions()
            except Exception as e:
                annots = list(page.annots())  # 转换为列表
                # + 白板画布
                if annots:
                    page.delete_annot(annots[-1])
                try:
                    # 使用白色填充矩形区域
                    page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                except Exception as e2:
                    print(f"创建白色画布时发生错误: {e2}")

                print(f"应用重编辑时发生错误: {e}")
                # continue



            if self.translation:
                page.insert_htmlbox(
                    rect,
                    translation_list[idx],
                    css=f"""
                    * {{
                        font-family: {get_font_by_language(self.target_language)};
                        font-size: auto;
                        color: #111111;
                        font-weight: normal;
                    }}
                    """
                )
            else:
                page.insert_htmlbox(
                    rect,
                    texts_list[idx],
                    css=f"* {{font-family:{get_font_by_language(self.target_language)}; font-size:auto; font-weight:normal;}}"
                )
if __name__ == '__main__':

    main_function(original_language='auto', target_language='zh', pdf_path='demo.pdf').main()