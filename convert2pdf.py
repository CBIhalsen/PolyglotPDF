import fitz
import os


def convert_to_pdf(input_file, output_file=None):
    """
    将支持的文档格式转换为 PDF，支持跨平台路径处理

    Args:
        input_file (str): 输入文件的完整路径
        output_file (str, optional): 输出PDF文件的完整路径。如果为None，则使用输入文件名+.pdf

    Returns:
        bool: 转换是否成功
    """
    try:
        # 规范化路径，处理不同平台的路径分隔符
        input_file = os.path.normpath(input_file)

        if not os.path.exists(input_file):
            print(f"错误：输入文件 '{input_file}' 不存在")
            return False

        # 如果未指定输出文件，则基于输入文件生成输出路径
        if output_file is None:
            # 获取文件名和目录
            file_dir = os.path.dirname(input_file)
            file_name = os.path.basename(input_file)
            name_without_ext = os.path.splitext(file_name)[0]

            # 在同一目录下创建同名PDF文件
            output_file = os.path.join(file_dir, f"{name_without_ext}.pdf")

        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        print(f"正在处理文件: {input_file}")
        print(f"输出文件将保存为: {output_file}")

        # 1. 先用 fitz.open 打开文档（EPUB、XPS、FB2 等格式）
        doc = fitz.open(input_file)
        print(f"文档页数: {len(doc)}")

        # 2. 调用 convert_to_pdf() 得到 PDF 格式字节流
        pdf_bytes = doc.convert_to_pdf()

        # 3. 再以 "pdf" 格式打开这段字节流
        pdf_doc = fitz.open("pdf", pdf_bytes)

        # 4. 保存为真正的 PDF 文件
        pdf_doc.save(output_file)

        # 关闭文档
        pdf_doc.close()
        doc.close()

        # 检查输出文件是否成功创建
        if os.path.exists(output_file):
            print(f"转换成功！PDF文件已保存为: {output_file}")
            return True
        else:
            print("转换似乎完成，但输出文件未找到")
            return False

    except fitz.FileDataError as e:
        print(f"文件格式错误或文件损坏：{str(e)}")
    except PermissionError as e:
        print(f"权限错误：无法访问或写入文件 - {str(e)}")
    except Exception as e:
        print(f"转换失败，错误类型: {type(e).__name__}")
        print(f"错误详情: {str(e)}")
        # 在调试模式下打印完整的堆栈跟踪
        import traceback
        traceback.print_exc()

    return False
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
