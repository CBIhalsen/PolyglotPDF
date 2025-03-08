import fitz
import os


def create_pdf_thumbnail(pdf_path, width=400):
    """
    为PDF文件第一页创建缩略图并保存到pdf_path上一层目录的thumbnail文件夹

    参数:
        pdf_path: PDF文件路径
        width: 缩略图的宽度（像素）
    """
    try:
        # 获取PDF文件名（不含扩展名）
        pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]

        # 获取PDF文件的绝对路径
        pdf_absolute_path = os.path.abspath(pdf_path)

        # 获取PDF文件所在目录的上一层目录
        parent_dir = os.path.dirname(os.path.dirname(pdf_absolute_path))

        # 构建保存缩略图的路径（上一层目录的thumbnail文件夹）
        thumbnail_dir = os.path.join(parent_dir, 'thumbnail')

        # 如果目录不存在，创建目录
        os.makedirs(thumbnail_dir, exist_ok=True)

        # 构建输出路径
        output_path = os.path.join(thumbnail_dir, f"{pdf_filename}.png")

        # 打开PDF文件
        doc = fitz.open(pdf_path)

        # 获取第一页
        first_page = doc[0]

        # 设置缩放参数
        zoom = width / first_page.rect.width
        matrix = fitz.Matrix(zoom, zoom)

        # 获取页面的像素图
        pix = first_page.get_pixmap(matrix=matrix, alpha=False)

        # 保存图片
        pix.save(output_path)

        # 关闭PDF文档
        doc.close()

        print(f"缩略图已保存到: {output_path}")
        return output_path

    except Exception as e:
        print(f"生成缩略图时发生错误: {str(e)}")
        return None


# 使用示例
if __name__ == "__main__":
    # PDF文件路径
    pdf_file = "g55.pdf"
    # 生成并保存缩略图
    thumbnail_path = create_pdf_thumbnail(pdf_file, width=400)
