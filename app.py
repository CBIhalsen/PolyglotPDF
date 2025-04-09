from flask import Flask, request, send_file, jsonify, send_from_directory
import json
from pathlib import Path

from threading import Thread
import atexit
import os
import sys
import webbrowser
from main import main_function
import load_config
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from load_config import delete_entry, decrease_count, get_default_services, update_default_services
from convert2pdf import convert_to_pdf
from threading import Timer
from socketserver import ThreadingMixIn
from werkzeug.serving import BaseWSGIServer, make_server


class ThreadedWSGIServer(ThreadingMixIn, BaseWSGIServer):
    """
    支持多线程处理的 WSGI Server。
    通过混入 ThreadingMixIn，让每个请求在单独的线程中处理，
    从而避免单请求长时间阻塞其它请求。
    """
    # 不需要额外的方法或属性，继承自 ThreadingMixIn 和 BaseWSGIServer 即可。
    pass

def get_app_data_dir():
    """获取应用数据目录，确保跨平台兼容性"""
    if getattr(sys, 'frozen', False):
        # 打包后的应用
        if sys.platform == 'darwin':  # macOS
            # 在macOS上使用用户的Application Support目录
            app_data = os.path.join(os.path.expanduser('~/Library/Application Support'), 'EbookTranslation')
        elif sys.platform == 'linux':  # Linux
            # 在Linux上使用~/.local/share目录
            app_data = os.path.join(os.path.expanduser('~/.local/share'), 'EbookTranslation')
        else:  # Windows或其他
            # 在Windows上使用应用程序所在目录
            app_data = os.path.dirname(sys.executable)
    else:
        # 开发环境
        app_data = os.path.dirname(os.path.abspath(__file__))

    # 确保目录存在
    os.makedirs(app_data, exist_ok=True)
    return app_data


# 在app.py开头附近添加这一行
APP_DATA_DIR = get_app_data_dir()

app = Flask(__name__, static_folder=None)  # 禁用默认的静态文件处理

CORS(app)

# 获取当前文件目录
current_dir = Path(APP_DATA_DIR)

# 设置上传文件目录
UPLOAD_DIR = os.path.join(APP_DATA_DIR, "static", "original")
TARGET_DIR = os.path.join(APP_DATA_DIR, "static", "target")

# 确保目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TARGET_DIR, exist_ok=True)

# 静态文件配置
app.static_folder = 'static'

# 创建线程池
executor = ThreadPoolExecutor(max_workers=13)

# 创建锁用于保护文件访问
file_lock = Lock()


@app.route('/static/<path:filename>')
def serve_static(filename):
    """提供静态文件访问，使用APP_DATA_DIR中的文件"""
    try:
        # 直接使用APP_DATA_DIR中的static目录
        static_dir = os.path.join(APP_DATA_DIR, 'static')
        print(f"Trying to serve: {os.path.join(static_dir, filename)}")  # 调试输出

        if os.path.exists(os.path.join(static_dir, filename)):
            return send_from_directory(static_dir, filename)
        else:
            print(f"File not found: {os.path.join(static_dir, filename)}")  # 调试输出
            return f"File not found: {filename}", 404

    except Exception as e:
        print(f"Error serving static file: {e}")  # 调试输出
        return str(e), 500


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

@app.route('/pdfviewer2.html')
def read_pdfviewer2():
    # 获取 URL 参数
    index = request.args.get('index')
    # print(index,'打开')

    # 现在你可以使用这些参数了
    load_config.update_file_status(index=int(index), read="1")
    return send_file(current_dir / "pdfviewer2.html")


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

        # 使用APP_DATA_DIR构建上传目录路径
        UPLOAD_DIR = os.path.join(APP_DATA_DIR, 'static', 'original')
        # 确保目录存在
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # 构建文件完整路径
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
                    "filename": pdf_filename  # 返回PDF文件名
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

        print(f"Processing files: {files}, target: {target_lang}, source: {original_lang}")

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
        print('删除', article_id)
        success = delete_entry(int(article_id)) and decrease_count()
        print('zzz', success)

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
        translation_open = data.get('translation')
        api_type = data.get('apiType')
        ocr_value = data.get('OCR')

        # 这里添加保存设置的逻辑
        # 例如保存到数据库或配置文件
        update_default_services(translation_open, api_type, ocr_value)  # 示例函数

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


# 修改 get_recent() 函数
@app.route('/recent.json')
def get_recent():
    try:
        data = load_config.load_recent()
        if data is None:
            return jsonify({})
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 修改 get_config() 函数
@app.route('/config_json', methods=['GET'])
def get_config_json():
    """
    前端页面首次加载时，会通过 GET /config_json 获取配置信息。
    返回的内容就是前端需要渲染的 config.json 数据结构。
    现在总是返回最新配置
    """
    config_data = load_config.load_config(force_reload=True)
    if config_data is None:
        return jsonify({}), 500
    return jsonify(config_data)

# 修改 update_config() 函数
@app.route('/update_config', methods=['POST'])
def update_config_json():
    """处理单个配置更新"""
    try:
        new_config = request.get_json()
        if not new_config:
            return jsonify({'status': 'error', 'message': '无效的配置数据'}), 400

        # 加载当前配置
        current_config = load_config.load_config()
        if current_config is None:
            return jsonify({'status': 'error', 'message': '无法加载当前配置'}), 500

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

# 修改 save_all() 函数
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


@app.route('/api/config', methods=['GET'])
def get_config_api():
    # 每次请求时强制重新加载配置
    config_data = load_config.load_config(force_reload=True)
    if config_data is None:
        return jsonify({}), 500
    return jsonify(config_data)

@app.route('/api/config', methods=['POST'])
def update_config_api():
    # 确保处理配置更新时能够正确处理grok相关的设置
    # 通常这个函数应该直接将接收到的数据写入config.json，所以如果前端已正确发送grok配置，不需要修改这里
    try:
        new_config = request.get_json()
        if not new_config:
            return jsonify({'status': 'error', 'message': '无效的配置数据'}), 400

        # 加载当前配置
        current_config = load_config.load_config()
        if current_config is None:
            return jsonify({'status': 'error', 'message': '无法加载当前配置'}), 500

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


@app.route("/translate_file", methods=["POST"])
def translate_file():
    try:
        # 翻译完成后确保更新状态
        if translation_type == "Grok":
            print("Grok translation completed, updating status")
        elif translation_type == "ThirdParty":
            print("ThirdParty translation completed, updating status")
        elif translation_type == "GLM":
            print("GLM translation completed, updating status")
        
        # 更新翻译状态为已完成
        update_translation_status(filename, '1')
        return jsonify({"status": "success", "message": "翻译完成"})
    except Exception as e:
        print(f"翻译过程中发生错误: {str(e)}")
        # 确保即使出错也更新状态，避免前端无限加载
        update_translation_status(filename, '0')
        return jsonify({"status": "error", "message": str(e)})

# 辅助函数：更新翻译状态
def update_translation_status(filename, status):
    """更新指定文件的翻译状态"""
    try:
        with open("recent.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for item in data:
            if item.get("name") == filename:
                item["statue"] = status
                break
        
        with open("recent.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"已更新文件 {filename} 的翻译状态为 {status}")
    except Exception as e:
        print(f"更新翻译状态时出错: {e}")

# 添加重新加载配置的路由
@app.route('/api/reload-config', methods=['POST'])
def reload_config():
    """
    强制重新加载配置文件
    
    Returns:
        Response: JSON响应，包含重新加载的结果
    """
    try:
        # 强制重新加载配置
        config = load_config.load_config(force_reload=True)
        if config is None:
            return jsonify({
                'success': False,
                'message': 'Failed to reload configuration'
            }), 500
            
        return jsonify({
            'success': True,
            'message': 'Configuration reloaded successfully',
            'config': config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error reloading configuration: {str(e)}'
        }), 500

server = None

class ServerThread(Thread):
    """后台运行的 Flask 服务器线程。"""
    def __init__(self, flask_app, host="127.0.0.1", port=12226):
        super().__init__()
        self.host = host
        self.port = port
        self.app = flask_app
        self.srv = None

    def run(self):
        # 使用自定义的多线程 WSGI Server
        self.srv = make_server(self.host, self.port, self.app, ThreadedWSGIServer)
        self.srv.serve_forever()

    def shutdown(self):
        if self.srv:
            self.srv.shutdown()


def open_browser():
    webbrowser.open_new("http://127.0.0.1:12226")
# 修改主程序初始化部分


@atexit.register
def on_exit():
    """Python 进程退出前，自动停止服务器。"""
    print("程序退出，准备停止服务器...")
    global server
    if server:
        server.shutdown()
        server.join()
        print("服务器已停止。")
if __name__ == "__main__":
    print(f"Application data directory: {APP_DATA_DIR}")
    print(f"Current directory: {current_dir}")
    print("Required files:")
    print(f"- index.html: {'✓' if (current_dir / 'index.html').exists() else '✗'}")

    # 延迟打开浏览器
    Timer(1, open_browser).start()

    try:
        # 创建并启动服务器
        server = ServerThread(app, host="127.0.0.1", port=12226)
        server.daemon = True  # 设置为守护线程
        server.start()
        print("服务器已在 http://127.0.0.1:12226 运行...")

        # 保持主线程运行
        while True:
            try:
                if not server.is_alive():
                    break
                server.join(1)  # 每秒检查一次服务器状态
            except KeyboardInterrupt:
                print("\n接收到终止信号，正在关闭服务器...")
                server.shutdown()
                break

    except Exception as e:
        print(f"运行时错误: {e}")
    finally:
        # 清理资源
        executor.shutdown(wait=True)
        if 'server' in locals() and server:
            server.shutdown()
