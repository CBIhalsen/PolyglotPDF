import fitz
import os

def merge_pdfs_horizontally(pdf1_path, pdf2_path, output_path, spacing=0):
    """
    水平合并两个PDF文件的所有页面
    :param pdf1_path: 第一个PDF文件的绝对路径
    :param pdf2_path: 第二个PDF文件的绝对路径
    :param output_path: 输出PDF文件的绝对路径
    :param spacing: 两个PDF之间的间距（点）
    """
    # 确保输入路径存在
    if not os.path.exists(pdf1_path):
        raise FileNotFoundError(f"找不到第一个PDF文件: {pdf1_path}")
    if not os.path.exists(pdf2_path):
        raise FileNotFoundError(f"找不到第二个PDF文件: {pdf2_path}")

    # 打开两个源PDF文件
    doc1 = fitz.open(pdf1_path)
    doc2 = fitz.open(pdf2_path)

    # 创建新的PDF文档
    result_doc = fitz.open()

    # 确保两个文档都至少有一页
    if doc1.page_count == 0 or doc2.page_count == 0:
        raise ValueError("Both PDFs must have at least one page")

    # 确保两个PDF的页数相同
    if doc1.page_count != doc2.page_count:
        raise ValueError("Both PDFs must have the same number of pages")

    # 处理每一页
    for page_num in range(doc1.page_count):
        # 获取两个PDF的当前页
        page1 = doc1[page_num]
        page2 = doc2[page_num]

        # 获取页面尺寸
        rect1 = page1.rect
        rect2 = page2.rect

        # 计算新页面的尺寸
        new_width = rect1.width + rect2.width + spacing
        new_height = max(rect1.height, rect2.height)

        # 创建新页面
        new_page = result_doc.new_page(width=new_width, height=new_height)

        # 创建第一个PDF的位置矩阵（保持在左侧）
        matrix1 = fitz.Matrix(1, 1)

        # 创建第二个PDF的位置矩阵（移动到右侧）
        matrix2 = fitz.Matrix(1, 1)
        x_shift = rect1.width + spacing
        matrix2.pretranslate(x_shift, 0)

        # 将两个页面内容复制到新页面
        new_page.show_pdf_page(rect1, doc1, page_num, matrix1)
        new_page.show_pdf_page(fitz.Rect(x_shift, 0, x_shift + rect2.width, new_height),
                               doc2, page_num, matrix2)

    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 保存结果
    result_doc.save(output_path)

    # 关闭所有文档
    doc1.close()
    doc2.close()
    result_doc.close()

# 使用示例
if __name__ == "__main__":
    pdf1_path = r"g6.pdf"
    pdf2_path = r"g6_zh.pdf"
    output_path = r"./output/merged.pdf"

    try:
        merge_pdfs_horizontally(pdf1_path, pdf2_path, output_path)
        print("PDFs merged successfully!")
        print(f"Output saved to: {output_path}")
    except FileNotFoundError as e:
        print(f"File error: {str(e)}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
