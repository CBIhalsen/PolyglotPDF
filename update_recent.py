import os
import json
import datetime
from typing import List, Dict, Any
import glob
from collections import OrderedDict
import re

def parse_merged_filename(filename: str) -> Dict[str, str]:
    """从合并PDF文件名解析出原始文件名、原始语言和目标语言"""
    # 格式为：原始文件名_原始语言_目标语言.pdf
    pattern = r"(.+)_(\w+)_(\w+)\.pdf$"
    match = re.match(pattern, filename)
    
    if match:
        original_name = match.group(1) + ".pdf"  # 添加.pdf后缀
        original_lang = match.group(2)
        target_lang = match.group(3)
        return {
            "original_name": original_name,
            "original_language": original_lang,
            "target_language": target_lang
        }
    else:
        # 如果不符合格式，返回默认值并确保有.pdf后缀
        name_without_ext = filename.rsplit(".", 1)[0]  # 去掉扩展名
        return {
            "original_name": name_without_ext + ".pdf",
            "original_language": "auto",
            "target_language": "zh"
        }

def get_file_info(file_path: str) -> Dict[str, Any]:
    """从文件路径获取文件信息"""
    filename = os.path.basename(file_path)
    creation_time = os.path.getctime(file_path)
    date_str = datetime.datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')
    
    # 解析文件名
    parsed_info = parse_merged_filename(filename)
    
    # 创建有序字典，确保属性按指定顺序排列
    ordered_info = OrderedDict()
    ordered_info["index"] = 0  # 临时值，会在后面被更新
    ordered_info["date"] = date_str
    ordered_info["name"] = parsed_info["original_name"]
    ordered_info["original_language"] = parsed_info["original_language"]
    ordered_info["target_language"] = parsed_info["target_language"]
    ordered_info["read"] = "0"  # 默认为未读
    ordered_info["statue"] = "1"  # 默认状态为1
    
    return ordered_info

def update_config_count(count: int) -> bool:
    """
    更新config.json中的count值为指定的数量
    
    Args:
        count: 要设置的count值
        
    Returns:
        bool: 操作是否成功
    """
    try:
        # 读取config.json文件
        config_path = "config.json"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            # 更新count值
            config["count"] = count
            
            # 写回文件
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            print(f"已更新config.json的count值为: {count}")
            return True
        else:
            print(f"错误: 找不到config.json文件")
            return False
    except Exception as e:
        print(f"更新config.json的count值时发生错误: {str(e)}")
        return False

def update_recent_json():
    """更新recent.json文件，先清空现有配置，然后从索引0开始重新生成"""
    # 从merged_pdf目录读取文件
    merged_path = os.path.join("static", "merged_pdf")
    
    # 不读取现有文件，直接创建一个空数组
    existing_entries = []
    
    # 扫描merged_pdf目录获取文件
    merged_files = glob.glob(os.path.join(merged_path, "*.pdf"))
    new_entries = []
    
    for file_path in merged_files:
        file_info = get_file_info(file_path)
        new_entries.append(file_info)
    
    # 从索引0开始分配
    for i, entry in enumerate(new_entries):
        entry["index"] = i 
    
    # 保存新生成的条目
    with open("recent.json", "w", encoding="utf-8") as f:
        json.dump(new_entries, f, ensure_ascii=False, indent=2)
    
    # 更新config.json中的count值为新条目的数量
    update_config_count(len(new_entries))
    
    print(f"已重置并更新recent.json")

if __name__ == "__main__":
    update_recent_json()
