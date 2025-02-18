
from flask import Flask, request, send_file, jsonify, send_from_directory

import json
from pathlib import Path
import os

from main import main_function
import load_config
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from load_config import delete_entry, decrease_count,get_default_services,update_default_services
from convert2pdf import convert_to_pdf
app = Flask(__name__)
CORS(app)

# 获取当前文件目录
current_dir = Path(__file__).parent

# 设置上传文件目录
UPLOAD_DIR = "static/original"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 静态文件配置
app.static_folder = 'static'

# 创建线程池
executor = ThreadPoolExecutor(max_workers=13)

# 创建锁用于保护文件访问
file_lock = Lock()




@app.route('/')
def read_index():
    return send_file(current_dir / "index.html")

@app.route('/pdfviewer.html')
def read_pdfviewer():
    # 获取 URL 参数
    index = request.args.get('index')
    # print(index,'打开')


    # 现在你可以使用这些参数了
    load_config.update_file_status(index=int(index), read="1")
    return send_file(current_dir / "pdfviewer.html")

@app.route('/recent.json')
def get_recent():
    try:
        with file_lock:
            with open(current_dir / "recent.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({})
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/upload/', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "message": "No file part"
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "success": False,
                "message": "No selected file"
            }), 400

        # 直接使用原始文件名，不使用 secure_filename
        filename = file.filename
        file_extension = os.path.splitext(filename)[1].lower()
        print(filename, '文件名')
        file_path = os.path.join(UPLOAD_DIR, filename)

        file.save(file_path)

        # 如果不是PDF，进行转换
        if file_extension != '.pdf':
            # 创建PDF文件名
            pdf_filename = os.path.splitext(filename)[0] + '.pdf'
            pdf_file_path = os.path.join(UPLOAD_DIR, pdf_filename)

            # 转换文件
            if convert_to_pdf(input_file=file_path, output_file=pdf_file_path):
                # 转换成功后删除原始文件
                os.remove(file_path)


                return jsonify({
                    "success": True,
                    "message": "文件已成功转换为PDF并保存",
                    "filename": filename
                })
            else:
                # 转换失败，删除原始文件
                os.remove(file_path)
                return jsonify({
                    "success": False,
                    "message": "PDF转换失败"
                }), 500
        else:
            # 如果是PDF文件，直接返回成功
            return jsonify({
                "success": True,
                "message": "PDF文件上传成功",
                "filename": filename
            })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"上传失败: {str(e)}"
        }), 500

@app.route('/translation', methods=['POST'])
def translate_files():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        files = data.get('files', [])
        if not files:
            return jsonify({"error": "No files provided"}), 400

        target_lang = data.get('targetLang', 'zh')
        original_lang = data.get('sourceLang', 'en')  # 默认改为 'en'

        print(f"Processing files: {files}, target: 3{target_lang}, source: 3{original_lang}")

        # 修改翻译任务的函数调用方式
        def translate_single_file(filename):
            try:
                # 直接使用 main_function 而不是 start
                translator = main_function(
                    original_language=original_lang,
                    target_language=target_lang,
                    pdf_path=filename
                )
                return translator.main()
            except Exception as e:
                print(f"Error translating {filename}: {str(e)}")
                return {"filename": filename, "error": str(e)}

        # 使用线程池并行处理翻译
        futures = []
        for filename in files:
            # 分离文件名和扩展名
            name, ext = os.path.splitext(filename)

            # 如果扩展名不是 .pdf，则改为 .pdf
            if ext.lower() != '.pdf':
                filename = name + '.pdf'
            print(f"Submitting translation task for: {filename}")
            future = executor.submit(translate_single_file, filename)
            futures.append(future)

        # 等待所有翻译任务完成并收集结果
        results = []
        for future in futures:
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Task execution error: {str(e)}")
                results.append({"error": str(e)})

        return jsonify({
            "status": "success",
            "message": "Translation tasks completed",
            "results": results
        })

    except Exception as e:
        print(f"Error in translate_files: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to process translation request: {str(e)}"
        }), 500
@app.route('/delete_article', methods=['POST'])
def delete_article():
    """
    处理删除文章的请求

    Returns:
        Response: JSON响应，包含删除操作的结果
    """
    try:
        # 从请求中获取文章ID
        data = request.get_json()
        article_id = data.get('articleId')

        if article_id is None:
            return jsonify({'error': 'Missing article ID'}), 400

        # 调用删除函数
        success = delete_entry(int(article_id)),decrease_count()

        if success:
            return jsonify({'message': 'Article deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete article'}), 500

    except Exception as e:
        print(f"Error deleting article: {str(e)}")
        return jsonify({'error': 'Server error'}), 500
@app.route('/delete_batch', methods=['POST'])
def delete_batch():
    """
    处理批量删除文章的请求
    :return: JSON 响应
    """
    try:
        data = request.get_json()
        # 前端传来一个数组，例如 { "articleIds": [1,3,5] }
        article_ids = data.get('articleIds', [])
        if not article_ids:
            return jsonify({'error': 'No article IDs provided'}), 400

        # 用于统计删除成功/失败的数量
        total = len(article_ids)
        success_count = 0
        failed_list = []

        for article_id in article_ids:
            try:
                # 调用单条删除函数
                success = delete_entry(int(article_id))
                if success:
                    # 如果删除成功也需要更新计数
                    decrease_count()  # 假设你有一个 decrease_count() 函数
                    success_count += 1
                else:
                    failed_list.append(article_id)
            except Exception as e:
                print(f"Error deleting article {article_id}: {str(e)}")
                failed_list.append(article_id)

        # 如果所有都成功，success_count == total
        return jsonify({
            'message': 'Batch delete attempted.',
            'total': total,
            'success_count': success_count,
            'failed_list': failed_list
        }), 200

    except Exception as e:
        print(f"Error in batch delete: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@app.route('/api/save-settings', methods=['POST'])
def save_settings():
    try:
        # 获取前端发送的JSON数据
        data = request.get_json()

        # 解析数据
        translation_open= data.get('translation')
        api_type = data.get('apiType')
        ocr_value = data.get('OCR')

        # 这里添加保存设置的逻辑
        # 例如保存到数据库或配置文件
        update_default_services(translation_open,api_type, ocr_value)  # 示例函数

        # 返回成功响应
        return jsonify({'message': '设置保存成功'}), 200

    except Exception as e:
        # 如果发生错误,返回错误响应
        return jsonify({'error': str(e)}), 500


@app.route('/api/get-default-services', methods=['GET'])
def get_default_services_route():


    """
    获取默认服务配置的API路由

    Returns:
        JSON响应，包含默认服务配置信息或错误信息
    """
    try:
        services = get_default_services()

        if services is None:
            return jsonify({
                'success': False,
                'message': 'Failed to get default services configuration'
            }), 400

        return jsonify({
            'success': True,
            'data': services
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/config_json', methods=['GET'])
def get_config():
    """
    前端页面首次加载时，会通过 GET /config_json 获取配置信息。
    返回的内容就是前端需要渲染的 config.json 数据结构。
    """
    config_data = load_config.load_config()
    return jsonify(config_data)





@app.route('/update_config', methods=['POST'])
def update_config():
    """处理单个配置更新"""
    try:
        new_config = request.get_json()
        if not new_config:
            return jsonify({'status': 'error', 'message': '无效的配置数据'}), 400

        # 加载当前配置
        current_config = load_config.load_config()

        # 递归更新配置
        def update_dict(current, new):
            for key, value in new.items():
                if isinstance(value, dict) and key in current and isinstance(current[key], dict):
                    update_dict(current[key], value)
                else:
                    current[key] = value

        update_dict(current_config, new_config)

        # 保存更新后的配置
        if load_config.save_config(current_config):
            return jsonify({'status': 'success', 'message': '配置已更新'}), 200
        else:
            return jsonify({'status': 'error', 'message': '保存配置失败'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/save_all', methods=['POST'])
def save_all():
    """完全覆盖保存所有配置"""
    try:
        new_config = request.get_json()
        if not new_config:
            return jsonify({'status': 'error', 'message': '无效的配置数据'}), 400

        # 直接保存新配置
        if load_config.save_config(new_config):
            return jsonify({'status': 'success', 'message': '所有配置已保存'}), 200
        else:
            return jsonify({'status': 'error', 'message': '保存配置失败'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == "__main__":
    print(f"Current directory: {current_dir}")
    print("Required files:")
    print(f"- index.html: {'✓' if (current_dir / 'index.html').exists() else '✗'}")
    print(f"- recent.json: {'✓' if (current_dir / 'recent.json').exists() else '✗'}")

    app.run(host="127.0.0.1", port=8000, debug=True)
