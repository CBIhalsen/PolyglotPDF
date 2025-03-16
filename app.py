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
import socket  # 新增，用于获取本机 IP

class ThreadedWSGIServer(ThreadingMixIn, BaseWSGIServer):
    """
    支持多线程处理的 WSGI Server。
    通过混入 ThreadingMixIn，让每个请求在单独的线程中处理，
    从而避免单请求长时间阻塞其它请求。
    """
    pass

def get_app_data_dir():
    """获取应用数据目录，确保跨平台兼容性"""
    if getattr(sys, 'frozen', False):
        if sys.platform == 'darwin':  # macOS
            app_data = os.path.join(os.path.expanduser('~/Library/Application Support'), 'EbookTranslation')
        elif sys.platform == 'linux':  # Linux
            app_data = os.path.join(os.path.expanduser('~/.local/share'), 'EbookTranslation')
        else:  # Windows 或其他
            app_data = os.path.dirname(sys.executable)
    else:
        app_data = os.path.dirname(os.path.abspath(__file__))

    os.makedirs(app_data, exist_ok=True)
    return app_data

# 获取本机局域网 IP 的函数
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))  # 连接外部地址以获取本地 IP
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'  # 如果获取失败，默认回退到本地回环地址
    finally:
        s.close()
    return ip

APP_DATA_DIR = get_app_data_dir()

app = Flask(__name__, static_folder=None)
CORS(app)

current_dir = Path(APP_DATA_DIR)
UPLOAD_DIR = os.path.join(APP_DATA_DIR, "static", "original")
TARGET_DIR = os.path.join(APP_DATA_DIR, "static", "target")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TARGET_DIR, exist_ok=True)

app.static_folder = 'static'
executor = ThreadPoolExecutor(max_workers=13)
file_lock = Lock()

@app.route('/static/<path:filename>')
def serve_static(filename):
    try:
        static_dir = os.path.join(APP_DATA_DIR, 'static')
        print(f"Trying to serve: {os.path.join(static_dir, filename)}")
        if os.path.exists(os.path.join(static_dir, filename)):
            return send_from_directory(static_dir, filename)
        else:
            print(f"File not found: {os.path.join(static_dir, filename)}")
            return f"File not found: {filename}", 404
    except Exception as e:
        print(f"Error serving static file: {e}")
        return str(e), 500

@app.route('/')
def read_index():
    return send_file(current_dir / "index.html")

@app.route('/pdfviewer.html')
def read_pdfviewer():
    index = request.args.get('index')
    load_config.update_file_status(index=int(index), read="1")
    return send_file(current_dir / "pdfviewer.html")

@app.route('/upload/', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "message": "No file part"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "message": "No selected file"}), 400

        filename = file.filename
        file_extension = os.path.splitext(filename)[1].lower()
        print(filename, '文件名')

        UPLOAD_DIR = os.path.join(APP_DATA_DIR, 'static', 'original')
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR, filename)
        file.save(file_path)

        if file_extension != '.pdf':
            pdf_filename = os.path.splitext(filename)[0] + '.pdf'
            pdf_file_path = os.path.join(UPLOAD_DIR, pdf_filename)
            if convert_to_pdf(input_file=file_path, output_file=pdf_file_path):
                os.remove(file_path)
                return jsonify({"success": True, "message": "文件已成功转换为PDF并保存", "filename": pdf_filename})
            else:
                os.remove(file_path)
                return jsonify({"success": False, "message": "PDF转换失败"}), 500
        else:
            return jsonify({"success": True, "message": "PDF文件上传成功", "filename": filename})

    except Exception as e:
        return jsonify({"success": False, "message": f"上传失败: {str(e)}"}), 500

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
        original_lang = data.get('sourceLang', 'en')

        print(f"Processing files: {files}, target: {target_lang}, source: {original_lang}")

        def translate_single_file(filename):
            try:
                translator = main_function(original_language=original_lang, target_language=target_lang, pdf_path=filename)
                return translator.main()
            except Exception as e:
                print(f"Error translating {filename}: {str(e)}")
                return {"filename": filename, "error": str(e)}

        futures = []
        for filename in files:
            name, ext = os.path.splitext(filename)
            if ext.lower() != '.pdf':
                filename = name + '.pdf'
            print(f"Submitting translation task for: {filename}")
            future = executor.submit(translate_single_file, filename)
            futures.append(future)

        results = []
        for future in futures:
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Task execution error: {str(e)}")
                results.append({"error": str(e)})

        return jsonify({"status": "success", "message": "Translation tasks completed", "results": results})

    except Exception as e:
        print(f"Error in translate_files: {str(e)}")
        return jsonify({"status": "error", "message": f"Failed to process translation request: {str(e)}"}), 500

@app.route('/delete_article', methods=['POST'])
def delete_article():
    try:
        data = request.get_json()
        article_id = data.get('articleId')
        if article_id is None:
            return jsonify({'error': 'Missing article ID'}), 400

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
    try:
        data = request.get_json()
        article_ids = data.get('articleIds', [])
        if not article_ids:
            return jsonify({'error': 'No article IDs provided'}), 400

        total = len(article_ids)
        success_count = 0
        failed_list = []

        for article_id in article_ids:
            try:
                success = delete_entry(int(article_id))
                if success:
                    decrease_count()
                    success_count += 1
                else:
                    failed_list.append(article_id)
            except Exception as e:
                print(f"Error deleting article {article_id}: {str(e)}")
                failed_list.append(article_id)

        return jsonify({'message': 'Batch delete attempted.', 'total': total, 'success_count': success_count, 'failed_list': failed_list}), 200
    except Exception as e:
        print(f"Error in batch delete: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@app.route('/api/save-settings', methods=['POST'])
def save_settings():
    try:
        data = request.get_json()
        translation_open = data.get('translation')
        api_type = data.get('apiType')
        ocr_value = data.get('OCR')
        update_default_services(translation_open, api_type, ocr_value)
        return jsonify({'message': '设置保存成功'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-default-services', methods=['GET'])
def get_default_services_route():
    try:
        services = get_default_services()
        if services is None:
            return jsonify({'success': False, 'message': 'Failed to get default services configuration'}), 400
        return jsonify({'success': True, 'data': services})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/recent.json')
def get_recent():
    try:
        data = load_config.load_recent()
        if data is None:
            return jsonify({})
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/config_json', methods=['GET'])
def get_config():
    config_data = load_config.load_config()
    if config_data is None:
        return jsonify({}), 500
    return jsonify(config_data)

@app.route('/update_config', methods=['POST'])
def update_config():
    try:
        new_config = request.get_json()
        if not new_config:
            return jsonify({'status': 'error', 'message': '无效的配置数据'}), 400

        current_config = load_config.load_config()
        if current_config is None:
            return jsonify({'status': 'error', 'message': '无法加载当前配置'}), 500

        def update_dict(current, new):
            for key, value in new.items():
                if isinstance(value, dict) and key in current and isinstance(current[key], dict):
                    update_dict(current[key], value)
                else:
                    current[key] = value

        update_dict(current_config, new_config)
        if load_config.save_config(current_config):
            return jsonify({'status': 'success', 'message': '配置已更新'}), 200
        else:
            return jsonify({'status': 'error', 'message': '保存配置失败'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/save_all', methods=['POST'])
def save_all():
    try:
        new_config = request.get_json()
        if not new_config:
            return jsonify({'status': 'error', 'message': '无效的配置数据'}), 400

        if load_config.save_config(new_config):
            return jsonify({'status': 'success', 'message': '所有配置已保存'}), 200
        else:
            return jsonify({'status': 'error', 'message': '保存配置失败'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

server = None

class ServerThread(Thread):
    def __init__(self, flask_app, host="0.0.0.0", port=12226):  # 修改为 0.0.0.0 支持局域网访问
        super().__init__()
        self.host = host
        self.port = port
        self.app = flask_app
        self.srv = None

    def run(self):
        self.srv = make_server(self.host, self.port, self.app, ThreadedWSGIServer)
        self.srv.serve_forever()

    def shutdown(self):
        if self.srv:
            self.srv.shutdown()

def open_browser():
    local_ip = get_local_ip()
    webbrowser.open_new(f"http://{local_ip}:12226")

@atexit.register
def on_exit():
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

    Timer(1, open_browser).start()

    try:
        local_ip = get_local_ip()
        server = ServerThread(app, host="0.0.0.0", port=12226)  # 绑定到 0.0.0.0
        server.daemon = True
        server.start()
        print(f"服务器已在 http://{local_ip}:12226 运行...")

        while True:
            try:
                if not server.is_alive():
                    break
                server.join(1)
            except KeyboardInterrupt:
                print("\n接收到终止信号，正在关闭服务器...")
                server.shutdown()
                break
    except Exception as e:
        print(f"运行时错误: {e}")
    finally:
        executor.shutdown(wait=True)
        if 'server' in locals() and server:
            server.shutdown()
