import os
import json
import datetime
from typing import List, Dict, Any
import glob
from collections import OrderedDict
import re
import shutil

def parse_merged_filename(filename: str) -> Dict[str, str]:
    """从合并PDF文件名解析出原始文件名、原始语言和目标语言"""
    # 格式为：原始文件名_原始语言_目标语言.pdf
    pattern = r"(.+)_([\w-]+)_([\w-]+)\.pdf$"
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

def validate_json_file(file_path: str) -> bool:
    """
    验证JSON文件格式是否正确
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        bool: 文件格式是否有效
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                json.load(f)
            return True
        return False
    except Exception as e:
        print(f"JSON文件格式无效: {str(e)}")
        return False

def update_recent_json():
    """更新recent.json文件，先清空现有配置，然后从索引0开始重新生成"""
    # 从merged_pdf目录读取文件
    merged_path = os.path.join("static", "merged_pdf")
    
    # 创建备份
    if os.path.exists("recent.json"):
        try:
            shutil.copy2("recent.json", "recent.json.bak")
            print(f"已创建备份文件: recent.json.bak")
        except Exception as e:
            print(f"创建备份文件失败: {str(e)}")
    
    # 扫描merged_pdf目录获取文件
    if not os.path.exists(merged_path):
        print(f"警告: 目录不存在 {merged_path}")
        try:
            os.makedirs(merged_path, exist_ok=True)
        except Exception as e:
            print(f"创建目录失败: {str(e)}")
    
    merged_files = glob.glob(os.path.join(merged_path, "*.pdf"))
    new_entries = []
    
    for file_path in merged_files:
        file_info = get_file_info(file_path)
        new_entries.append(file_info)
    
    # 从索引0开始分配
    for i, entry in enumerate(new_entries):
        entry["index"] = i 
    
    # 保存前先验证数据格式
    try:
        # 使用json.dumps检查序列化是否正常
        json_str = json.dumps(new_entries, ensure_ascii=False, indent=2)
        
        # 写入文件
        with open("recent.json", "w", encoding="utf-8") as f:
            f.write(json_str)
        
        # 验证写入的文件
        if not validate_json_file("recent.json"):
            raise Exception("写入的JSON文件验证失败")
        
        # 更新config.json中的count值为新条目的数量
        update_config_count(len(new_entries))
        
        print(f"已重置并更新recent.json，共 {len(new_entries)} 条记录")
    except Exception as e:
        print(f"更新recent.json文件失败: {str(e)}")
        # 尝试恢复备份
        if os.path.exists("recent.json.bak"):
            try:
                shutil.copy2("recent.json.bak", "recent.json")
                print("已从备份恢复recent.json文件")
            except Exception as e2:
                print(f"从备份恢复失败: {str(e2)}")

if __name__ == "__main__":
    update_recent_json()
