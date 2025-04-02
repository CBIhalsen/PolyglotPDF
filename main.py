
import All_Translation as at
from PIL import Image
import pytesseract
import time
import fitz
import os

import load_config

from datetime import datetime
import pdf_thumbnail
from load_config import APP_DATA_DIR
import get_new_blocks as new_blocks
import Subset_Font
import merge_pdf
config = load_config.load_config()
translation_type = config['default_services']['Translation_api']
translation = config['default_services']['Enable_translation']
use_mupdf = not config['default_services']['ocr_model']

PPC = config['PPC']
print('ppc',PPC)

# print(use_mupdf,'mupdf值')
# print('当前',config['count'])


def decimal_to_hex_color(decimal_color):
    if decimal_color == 0:
        return '#000000'  # 黑色

    # 将十进制数转换为十六进制，并移除'0x'前缀
    hex_color = hex(decimal_color)[2:]

    # 确保是6位十六进制数
    hex_color = hex_color.zfill(6)

    # 添加'#'前缀
    return f'#{hex_color}'

def is_math(text, page_num,font_info):
    return False

def line_non_text(text):
    return True


def is_non_text(text):
    return False

class main_function:
    def __init__(self, pdf_path,
                 original_language, target_language,bn = None,en = None,
                 DPI=72,):
        """
        这里的参数与原来保持一致或自定义。主要多加一个 self.pages_data 用于存储所有页面的提取结果。
        """

        self.pdf_path = pdf_path
        self.pdf_path = pdf_path
        self.full_path = os.path.join(APP_DATA_DIR, 'static', 'original', pdf_path)
        self.doc = fitz.open(self.full_path)

        self.original_language = original_language
        self.target_language = target_language
        self.DPI = DPI
        self.translation = translation
        self.translation_type = translation_type
        self.use_mupdf = use_mupdf
        self.line_model = line_model
        self.bn = bn
        self.en = en

        self.t = time.time()
        # 新增一个全局列表，用于存所有页面的 [文本, bbox]，以及翻译后结果
        # 形式: self.pages_data[page_index] = [ [原文, bbox], [原文, bbox], ... ]
        self.pages_data = []

    def main(self):
        """
        主流程函数。只做“计数更新、生成缩略图、建条目”等老逻辑，替换原来在这里的逐页翻译写入。
        但是保留 if use_mupdf: for... self.start(...) else: for... self.start(...)
        不做“翻译和写入”的动作，而是只做“提取文本”。
        提取完所有页面后，批量翻译，再统一写入 PDF。
        """
        # 1. 计数和配置信息
        load_config.update_count()
        config = load_config.load_config()
        count = config["count"]


        # 2. 生成 PDF 缩略图 (保留原逻辑)
        pdf_thumbnail.create_pdf_thumbnail(self.full_path, width=400)

        # 3. 创建新条目（保留原逻辑）
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

        # 4. 保留原先判断是否 use_mupdf 的代码，以便先提取文本
        page_count =self.doc.page_count
        if self.bn == None:
            self.bn = 0
        if self.en == None:
            self.en = page_count

        if self.use_mupdf:
            start_page = self.bn
            end_page = min(self.en, page_count)

            # 使用 PyMuPDF 直接获取文本块
            for i in range(start_page, end_page):
                self.start(image=None, pag_num=i)  # 只做提取，不做翻译写入
        else:
            # OCR 模式
            zoom = self.DPI / 72
            mat = fitz.Matrix(zoom, zoom)
            # 处理从 self.bn 到 self.en 的页面范围，并确保 self.en 不超过文档页数
            start_page = self.bn
            end_page = min(self.en, page_count)

            # 迭代指定范围的页面
            for i in range(start_page, end_page):
                page = self.doc[i]  # 获取指定页面
                pix = page.get_pixmap(matrix=mat)
                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                # 如果需要保存图像到文件，可自行保留或注释
                # image.save(f'page_{i}.jpg', 'JPEG')
                self.start(image=image, pag_num=i)  # 只做提取，不做翻译写入

        # 5. 若开启翻译，则批量翻译所有提取的文本

        self.batch_translate_pages_data(
                original_language=self.original_language,
                target_language=self.target_language,
                translation_type=self.translation_type,
                batch_size=PPC
            )
        # 6. 子集化字体
        bold_text = ""
        normal_text = ""

        # 遍历所有页码
        for page in self.pages_data:
            for item in page:
                text = item[0]  # 原始文本
                translate_text = item[2]  # 翻译文本
                is_bold = item[6]  # text_bold值

                if is_bold:
                    bold_text += translate_text + " "  # 在每个文本之间添加空格
                else:
                    normal_text += translate_text + " "

        # 去除末尾多余的空格
        bold_text = bold_text.strip()
        normal_text = normal_text.strip()

        # 打印结果
        if bold_text:  # 如果粗体文本不为空
            in_font_path = os.path.join(APP_DATA_DIR, 'temp', 'fonts', f"{self.target_language}_bold.ttf")
            out_font_path = os.path.join(APP_DATA_DIR, 'temp', 'fonts', f"{self.target_language}_bold_subset.ttf")
            self.subset_font(in_font_path=in_font_path, out_font_path=out_font_path, text=bold_text)

            in_font_path2 = os.path.join(APP_DATA_DIR, 'temp', 'fonts', f"{self.target_language}.ttf")
            out_font_path2 = os.path.join(APP_DATA_DIR, 'temp', 'fonts', f"{self.target_language}_subset.ttf")
            self.subset_font(in_font_path=in_font_path2, out_font_path=out_font_path2, text=normal_text)

        else:
            in_font_path = os.path.join(APP_DATA_DIR, 'temp', 'fonts', f"{self.target_language}.ttf")
            out_font_path = os.path.join(APP_DATA_DIR, 'temp', 'fonts', f"{self.target_language}_subset.ttf")
            self.subset_font(in_font_path=in_font_path, out_font_path=out_font_path, text=normal_text)



        # 7. 将翻译结果统一写入 PDF（覆盖+插入译文）
        self.apply_translations_to_pdf()

        # 8. 保存 PDF、更新状态
        pdf_name, _ = os.path.splitext(self.pdf_path)
        target_path = os.path.join(APP_DATA_DIR, 'static', 'target', f"{pdf_name}_{self.target_language}.pdf")
        self.doc.ez_save(
            target_path,
            garbage=4,
            deflate=True
        )

        load_config.update_file_status(count, statue="1")  # statue = "1"

        # 8. 打印耗时
        end_time = time.time()
        print('翻译共耗时',end_time - self.t)
        merged_output_path = os.path.join(APP_DATA_DIR, 'static', 'merged_pdf', f"{pdf_name}_{self.original_language}_{self.target_language}.pdf")

        merge_pdf.merge_pdfs_horizontally(pdf1_path=self.pdf_path,pdf2_path=target_path,output_path=merged_output_path)

    def start(self, image, pag_num):
        """
        原先逐页处理的函数，现仅负责“提取文本并存储在 self.pages_data[pag_num]”。
        不在这里直接翻译或写回 PDF。
        """
        # 确保 self.pages_data 有 pag_num 对应的列表
        while len(self.pages_data) <= pag_num:
            self.pages_data.append([])  # 每个元素是 [ [text, (x0,y0,x1,y1)], ... ]

        page = self.doc.load_page(pag_num)

        if self.use_mupdf and image is None:
            blocks = new_blocks.get_new_blocks(page)
            for block in blocks:
                text_type = block[2]  # 类型
                if text_type == 'math':
                    continue
                else:
                    text = block[0]  # 文本内容
                    text_bbox = block[1]  # 边界框坐标
                    text_angle = block[3]
                    text_color = block[4]
                    text_indent = block[5]
                    text_bold = block[6]
                    text_size = block[7]
                    # 转换颜色值
                    html_color = decimal_to_hex_color(text_color)
                    self.pages_data[pag_num].append(
                        [text, tuple(text_bbox), None, text_angle,html_color,text_indent,text_bold,text_size])


        else:
            # OCR 提取文字
            config = load_config.load_config()
            tesseract_path = config['ocr_services']['tesseract']['path']
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

            Full_width, Full_height = image.size
            ocr_result = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

            current_paragraph_text = ''
            paragraph_bbox = {
                'left': float('inf'),
                'top': float('inf'),
                'right': 0,
                'bottom': 0
            }
            current_block_num = None
            Threshold_width = 0.06 * Full_width
            Threshold_height = 0.006 * Full_height

            for i in range(len(ocr_result['text'])):
                block_num = ocr_result['block_num'][i]
                text_ocr = ocr_result['text'][i].strip()
                left = ocr_result['left'][i]
                top = ocr_result['top'][i]
                width = ocr_result['width'][i]
                height = ocr_result['height'][i]

                if text_ocr and not is_math(text_ocr, pag_num, font_info='22') and not is_non_text(text_ocr):

                    # 若换 block 或段落间隔较大，则保存上一段
                    if (block_num != current_block_num or
                       (abs(left - paragraph_bbox['right']) > Threshold_width and
                        abs(height - (paragraph_bbox['bottom'] - paragraph_bbox['top'])) > Threshold_height and
                        abs(left - paragraph_bbox['left']) > Threshold_width)):

                        if current_paragraph_text:
                            # 转换到 PDF 坐标
                            Full_rect = page.rect
                            w_points = Full_rect.width
                            h_points = Full_rect.height

                            x0_ratio = paragraph_bbox['left'] / Full_width
                            y0_ratio = paragraph_bbox['top'] / Full_height
                            x1_ratio = paragraph_bbox['right'] / Full_width
                            y1_ratio = paragraph_bbox['bottom'] / Full_height

                            x0_pdf = x0_ratio * w_points
                            y0_pdf = y0_ratio * h_points
                            x1_pdf = x1_ratio * w_points
                            y1_pdf = y1_ratio * h_points

                            self.pages_data[pag_num].append([
                                current_paragraph_text.strip(),
                                (x0_pdf, y0_pdf, x1_pdf, y1_pdf)
                            ])

                        # 重置
                        current_paragraph_text = ''
                        paragraph_bbox = {
                            'left': float('inf'),
                            'top': float('inf'),
                            'right': 0,
                            'bottom': 0
                        }
                        current_block_num = block_num

                    # 继续累加文本
                    current_paragraph_text += text_ocr + " "
                    paragraph_bbox['left'] = min(paragraph_bbox['left'], left)
                    paragraph_bbox['top'] = min(paragraph_bbox['top'], top)
                    paragraph_bbox['right'] = max(paragraph_bbox['right'], left + width)
                    paragraph_bbox['bottom'] = max(paragraph_bbox['bottom'], top + height)

            # 收尾：最后一段存入
            if current_paragraph_text:
                Full_rect = page.rect
                w_points = Full_rect.width
                h_points = Full_rect.height

                x0_ratio = paragraph_bbox['left'] / Full_width
                y0_ratio = paragraph_bbox['top'] / Full_height
                x1_ratio = paragraph_bbox['right'] / Full_width
                y1_ratio = paragraph_bbox['bottom'] / Full_height

                x0_pdf = x0_ratio * w_points
                y0_pdf = y0_ratio * h_points
                x1_pdf = x1_ratio * w_points
                y1_pdf = y1_ratio * h_points

                self.pages_data[pag_num].append([
                    current_paragraph_text.strip(),
                    (x0_pdf, y0_pdf, x1_pdf, y1_pdf),
                    None
                ])

        # 注意：这里不做翻译、不插入 PDF，只负责“收集文本”到 self.pages_data

    def batch_translate_pages_data(self, original_language, target_language,
                                   translation_type, batch_size=PPC ):
        """PPC (Pages Per Call)
        分批翻译 pages_data，每次处理最多 batch_size 页的文本，避免一次性过多。
        将译文存回 self.pages_data 的第三个元素，如 [原文, bbox, 译文]
        """
        total_pages = len(self.pages_data)
        start_idx = 0

        while start_idx < total_pages:
            end_idx = min(start_idx + batch_size, total_pages)

            # 收集该批次的所有文本
            batch_texts = []
            for i in range(start_idx, end_idx):
                for block in self.pages_data[i]:
                    batch_texts.append(block[0])  # block[0] = 原文

            # 翻译


            if self.translation and use_mupdf:
                translation_list = at.Online_translation(
                    original_language=original_language,
                    target_language=target_language,
                    translation_type=translation_type,
                    texts_to_process=batch_texts
                ).translation()

            else:
                translation_list = batch_texts



            # 回填译文
            idx_t = 0
            for i in range(start_idx, end_idx):
                for block in self.pages_data[i]:
                    # 在第三个位置添加翻译文本
                    block[2] = translation_list[idx_t]
                    idx_t += 1

            start_idx += batch_size
            print('当前进度',end_idx,"/",total_pages)

    def apply_translations_to_pdf(self):
        """
        统一对 PDF 做“打码/打白 + 插入译文”操作
        """
        for page_index, blocks in enumerate(self.pages_data):
            page = self.doc.load_page(page_index)

            for block in blocks:
                coords = block[1]  # (x0, y0, x1, y1)
                # 如果第三个元素是译文，则用之，否则用原文
                translated_text = block[2]
                html_color = block[4]
                text_indent = block[5]
                text_bold = block[6]
                angle = block[3]
                text_size = float(block[7]) + 3

                rect = fitz.Rect(*coords)

                # 先尝试使用 Redact 遮盖
                try:
                    page.add_redact_annot(rect)
                    page.apply_redactions()
                except Exception as e:
                    # 若 Redact 失败，改用白色方块覆盖
                    annots = list(page.annots() or [])
                    if annots:
                        page.delete_annot(annots[-1])
                    try:
                        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                    except Exception as e2:
                        print(f"创建白色画布时发生错误: {e2}")
                    print(f"应用重编辑时发生错误: {e}")
                if text_bold:
                    # 字体族名称应该简单且不包含路径
                    font_family = f"{self.target_language}_bold_font"
                    font_path = os.path.join(APP_DATA_DIR, 'temp', 'fonts', f"{self.target_language}_bold_subset.ttf")
                else:
                    font_family = f"{self.target_language}_font"
                    font_path = os.path.join(APP_DATA_DIR, 'temp', 'fonts', f"{self.target_language}_subset.ttf")

                # 确保字体文件存在
                if not os.path.exists(font_path):
                    print(f"警告：字体文件不存在: {font_path}")

                # 使用绝对路径，确保路径分隔符正确
                font_path = font_path.replace('\\', '/')

                page.insert_htmlbox(
                    rect,
                    translated_text,
                    css=f"""
                    @font-face {{
                        font-family: "{font_family}";
                        src: url("{font_path}");
                    }}
                    * {{
                        font-family: "{font_family}";
                        color: {html_color};
                        text-indent: {text_indent}pt;  
                        font-size: {text_size}pt; 
                    }}
                    """,
                    rotate=angle
                )


    def subset_font(self, in_font_path, out_font_path,text):
        Subset_Font.subset_font(in_font_path=in_font_path,out_font_path=out_font_path,text=text,language=self.target_language)

if __name__ == '__main__':

    main_function(original_language='auto', target_language='zh', pdf_path='g2.pdf').main()