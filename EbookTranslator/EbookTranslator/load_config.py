import os
import json
import requests
from pathlib import Path
from typing import Optional, Dict


def get_working_dir() -> Path:
    """
    获取工作目录
    返回当前工作目录（即命令行执行目录或调用脚本所在目录）
    """
    return Path.cwd()


# 定义应用数据目录
WORKING_DIR = get_working_dir()
APP_DATA_DIR = WORKING_DIR  # 示例：将 APP_DATA_DIR 定义为工作目录
print(f"Working directory: {WORKING_DIR}")


def resolve_path(path: str) -> Path:
    """
    解析路径，支持绝对路径、相对路径和文件名。

    Args:
        path (str): 输入路径，可以是绝对路径、相对路径或文件名。

    Returns:
        Path: 解析后的完整路径。
    """
    # 如果 path 是绝对路径，直接返回
    if Path(path).is_absolute():
        return Path(path)

    # 如果 path 是相对路径或文件名，与 APP_DATA_DIR 拼接
    return APP_DATA_DIR / path


def load_config(config_path: Optional[str] = None) -> Optional[Dict]:
    """
    加载主配置文件，优先使用传入的 config_path 路径。
    如果未传入或路径无效，则尝试使用 APP_DATA_DIR 中的文件。
    如果 APP_DATA_DIR 中也没有 config.json，则从指定 URL 下载。

    Args:
        config_path (Optional[str]): 配置文件路径，可以是绝对路径、相对路径或文件名。

    Returns:
        Dict: 配置数据，如果加载失败则返回 None。
    """
    try:
        # 如果传入了 config_path 参数，优先使用
        if config_path:
            config_path = resolve_path(config_path)  # 解析路径
            if config_path.exists():
                with config_path.open("r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                print(f"Specified config path does not exist: {config_path}")

        # 如果没有传入 config_path 或路径无效，则使用 APP_DATA_DIR 中的 config.json
        app_config_path = APP_DATA_DIR / "config.json"
        if app_config_path.exists():
            with app_config_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # 如果 APP_DATA_DIR 中没有，则尝试从指定 URL 下载 config.json
            url = "https://raw.githubusercontent.com/CBIhalsen/PolyglotPDF/refs/heads/main/config.json"
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                # 将下载的内容保存到 APP_DATA_DIR
                APP_DATA_DIR.mkdir(parents=True, exist_ok=True)  # 确保 APP_DATA_DIR 存在
                print(
                    f"config.json file not found, downloading config.json from: {url}"
                )
                with app_config_path.open("w", encoding="utf-8") as f:
                    f.write(response.text)
                return response.json()
            else:
                print(f"Failed to download config.json, HTTP status code: {response.status_code}")
                return None
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return None


def get_file_path(filename: str) -> Path:
    """
    获取配置文件的完整路径，优先使用 APP_DATA_DIR 中的文件。

    Args:
        filename (str): 配置文件名。

    Returns:
        Path: 配置文件的完整路径。
    """
    # 首先检查 APP_DATA_DIR 中是否有该文件
    app_data_file = APP_DATA_DIR / filename
    if app_data_file.exists():
        return app_data_file

    # 如果 APP_DATA_DIR 中没有，则使用当前脚本所在目录的文件
    return Path(__file__).parent / filename
