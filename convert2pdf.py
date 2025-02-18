import fitz
import os


def convert_to_pdf(input_file, output_file=None):
    """ 将支持的文档格式转换为 PDF """

    if not os.path.exists(input_file):
        print(f"错误：输入文件 '{input_file}' 不存在")
        return

    try:
        if output_file is None:
            output_file = os.path.splitext(input_file)[0] + '.pdf'

        print(f"正在处理文件: {input_file}")

        # 1. 先用 fitz.open 打开 EPUB（或 XPS、FB2 等其他格式）
        doc = fitz.open(input_file)
        print(f"文档页数: {len(doc)}")

        # 2. 调用 convert_to_pdf() 得到 PDF 格式字节流
        pdf_bytes = doc.convert_to_pdf()

        # 3. 再以 “pdf” 格式打开这段字节流
        pdf_doc = fitz.open("pdf", pdf_bytes)

        # 4. 保存为真正的 PDF 文件
        pdf_doc.save(output_file)

        # 关闭文档
        pdf_doc.close()
        doc.close()

        if os.path.exists(output_file):
            print(f"转换成功！PDF文件已保存为: {output_file}")
        else:
            print("转换似乎完成，但输出文件未找到")

    except fitz.FileDataError as e:
        print(f"文件格式错误或文件损坏：{str(e)}")
    except PermissionError:
        print("权限错误：无法访问或写入文件")
    except Exception as e:
        print(f"转换失败，错误类型: {type(e).__name__}")
        print(f"错误详情: {str(e)}")
    return True
# 使用示例
if __name__ == "__main__":
    # 单个文件转换示例
    input_file = "666 (1).epub"

    # 验证文件扩展名
    if not input_file.lower().endswith(('.xps', '.epub', '.fb2', '.cbz', '.mobi')):
        print(f"不支持的文件格式。支持的格式包括: XPS, EPUB, FB2, CBZ, MOBI")
    else:
        convert_to_pdf(input_file)

    # 批量转换示例
    # input_directory = "documents"
    # batch_convert_to_pdf(input_directory)
