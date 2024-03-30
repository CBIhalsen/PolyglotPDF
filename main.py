from pdf2image import convert_from_path
import All_Translation as at

import pytesseract
import time
# import YoudaoTranslate as yt
import fitz
import os
import download_model
class main_function:

    def __init__(self,original_language,target_language,pdf_path,translation= True,key_deepl= '',DPI=150,):


        self.original_language = original_language
        self.target_language = target_language
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.pages = convert_from_path(pdf_path, DPI)  # 第二个参数是DPI（点每英寸）
        self.t = time.time()
        self.translation = translation
        self.key_deepl = key_deepl


    def main(self,):
    # 遍历每一页
        for i, page in enumerate(self.pages):
            # 可以选择保存图像到文件，也可以直接在内存中处理
            # page.save(f'1page_{i}.jpg', 'JPEG')
            self.start(image=page, pag_num=i)

    # 使用 os.path.splitext() 来分割路径和扩展名
        pdf_name, _ = os.path.splitext(self.pdf_path)
        self.doc.ez_save(f"{pdf_name}_{self.target_language}.pdf", garbage=4, deflate=True)

        e = time.time()
        print(e - self.t)

    def start(self,image, pag_num):

        text_rect = []
        # 指定tesseract.exe的安装路径

        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows示例路径
        # pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Linux/Mac示例路径

        # 获取图片的尺寸
        Full_width, Full_height = image.size

        # 使用pytesseract进行文字识别，获取详细的OCR结果
        ocr_result = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

        # 初始化变量来存储当前段落的信息
        current_paragraph_text = ''
        current_block_num = 0
        last_block_left = 0  # 存储上一个文本块的左边界
        last_block_right = 0  # 存储上一个文本块的右边界
        last_block_height = 0  # 存储上一个文本块的高度
        # 初始化段落的边界框坐标
        paragraph_bbox = {'left': float('inf'), 'top': float('inf'), 'right': 0, 'bottom': 0}
        Threshold_width = 0.06 * Full_width
        Threshold_height = 0.006 * Full_height
        # print(Threshold_width, Threshold_height)
        # 遍历结果
        for i in range(len(ocr_result['text'])):
            block_num = ocr_result['block_num'][i]
            text = ocr_result['text'][i].strip()
            left = ocr_result['left'][i]
            top = ocr_result['top'][i]
            width = ocr_result['width'][i]
            height = ocr_result['height'][i]

            # 判断是否开始新段落的条件
            if block_num != current_block_num or (abs(left - last_block_right) > Threshold_width and abs(
                    height - last_block_height) > Threshold_height and abs(left - last_block_left) > Threshold_width):

                # 如果当前段落文本不为空，则打印当前段落的信息和坐标
                if current_paragraph_text != '':
                    # 计算并打印坐标相对于图片尺寸的比值
                    x0_ratio = paragraph_bbox['left'] / Full_width
                    y0_ratio = paragraph_bbox['top'] / Full_height
                    x1_ratio = paragraph_bbox['right'] / Full_width
                    y1_ratio = paragraph_bbox['bottom'] / Full_height
                    # 坐标
                    # print(f'Coordinates Ratio: x0: {x0_ratio}, y0: {y0_ratio}, x1: {x1_ratio}, y1: {y1_ratio}\n')

                    page = self.doc.load_page(pag_num)  # 添加一个新页面

                    Full_rect = page.rect  # 获取页面的矩形尺寸
                    width_points = Full_rect.width  # 页面宽度，以点为单位
                    height_points = Full_rect.height  # 页面高度，以点为单位
                    # print(width_points, height_points)

                    coordinates_ratio = (x0_ratio, y0_ratio, x1_ratio, y1_ratio)
                    x0_pdf = coordinates_ratio[0] * width_points
                    y0_pdf = coordinates_ratio[1] * height_points
                    x1_pdf = coordinates_ratio[2] * width_points
                    y1_pdf = coordinates_ratio[3] * height_points

                    text_rect.append([current_paragraph_text, (x0_pdf, y0_pdf, x1_pdf, y1_pdf)])
                    # time.sleep(1)
                    # page.insert_htmlbox(rect,  translation_text, css="* {font-family:AdobeSongStd-Light;font-size:30px;}")

                    # 重置段落信息
                    current_paragraph_text = ''
                    paragraph_bbox = {'left': float('inf'), 'top': float('inf'), 'right': 0, 'bottom': 0}

                current_block_num = block_num

            if text:
                current_paragraph_text += text + ' '
                # 更新段落的边界框坐标
                last_block_left = paragraph_bbox['left']

                paragraph_bbox['left'] = min(paragraph_bbox['left'], left)
                paragraph_bbox['top'] = min(paragraph_bbox['top'], top)
                paragraph_bbox['right'] = max(paragraph_bbox['right'], left + width)
                paragraph_bbox['bottom'] = max(paragraph_bbox['bottom'], top + height)
                # 更新最后一个文本块的左,右边界和高度
                last_block_right = left + width
                last_block_height = height

        # 打印最后一个段落的信息和坐标（如果有）
        if current_paragraph_text:
            # print(f'Paragraph {current_block_num}: {current_paragraph_text}')
            # print(f'Coordinates: {paragraph_bbox}')
            # 计算并打印坐标相对于图片尺寸的比值
            x0_ratio = paragraph_bbox['left'] / Full_width
            y0_ratio = paragraph_bbox['top'] / Full_height
            x1_ratio = paragraph_bbox['right'] / Full_width
            y1_ratio = paragraph_bbox['bottom'] / Full_height
            # 坐标
            # print(f'Coordinates Ratio: x0: {x0_ratio}, y0: {y0_ratio}, x1: {x1_ratio}, y1: {y1_ratio}\n')
            page = self.doc.load_page(pag_num)  # 添加一个新页面

            Full_rect = page.rect  # 获取页面的矩形尺寸
            width_points = Full_rect.width  # 页面宽度，以点为单位
            height_points = Full_rect.height  # 页面高度，以点为单位
            # print(width_points, height_points)

            coordinates_ratio = (x0_ratio, y0_ratio, x1_ratio, y1_ratio)
            x0_pdf = coordinates_ratio[0] * width_points
            y0_pdf = coordinates_ratio[1] * height_points
            x1_pdf = coordinates_ratio[2] * width_points
            y1_pdf = coordinates_ratio[3] * height_points

            text_rect.append([current_paragraph_text, (x0_pdf, y0_pdf, x1_pdf, y1_pdf)])

        first_strings = []
        texts_list = [item[0] for item in text_rect]
        if self.translation:
            # translation_list = at.Offline_translation(original_language=self.original_language,target_language=self.target_language,
            #                                           texts_to_process=texts_list).translation()

            translation_list = at.Online_translation(original_language=self.original_language,target_language=self.target_language,key_deepl=self.key_deepl,texts_to_process=texts_list).deepl_translation()


        # 遍历text_rect
        for idx, item in enumerate(text_rect):
            # 打印元素的第一个字符串、四个坐标和指针
            # print(f"元素 {idx}:")
            # print("第一个字符串:", item[0])
            # print("四个坐标:", item[1])

            # 将第一个字符串添加到新的列表中
            first_strings.append(item[0])
            rect = fitz.Rect(item[1][0], item[1][1], item[1][2], item[1][3])
            page.add_redact_annot(rect)
            page.apply_redactions()  # empties the rect area
            # translation_text = item[0]
            if self.translation:
                page.insert_htmlbox(rect, translation_list[idx],
                                    css="* {font-family:AdobeSongStd-Light;font-size:30px;}")
            else:
                page.insert_htmlbox(rect, texts_list[idx],
                                    css="* {font-family:AdobeSongStd-Light;font-size:30px;}")



key_deepl = ''  # 请替换为你的deepl密钥 Please replace it with your deepl key
main_function(original_language='en',target_language='zh',pdf_path='66.pdf',translation=False,key_deepl=key_deepl).main()