
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import fitz  # PyMuPDF 的库名是 fitz
import math
import datetime
import re
import unicodedata
from collections import defaultdict

MATH_FONTS_SET = {
    "CMMI", "CMSY", "CMEX", "CMMI5", "CMMI6", "CMMI7", "CMMI8", "CMMI9", "CMMI10",
    "CMSY5", "CMSY6", "CMSY7", "CMSY8", "CMSY9", "CMSY10",
    "CMEX5", "CMEX6", "CMEX7", "CMEX8", "CMEX9", "CMEX10",  # 新增CMEX字体家族
    "MSAM", "MSBM", "EUFM", "EUSM", "TXMI", "TXSY", "PXMI", "PXSY",
    "CambriaMath", "AsanaMath", "STIXMath", "XitsMath", "Latin Modern Math",
    "Neo Euler", 'MTMI', 'MTSYN'
}


def snap_angle_func(raw_angle):
    """
    将原始角度吸附到最接近的 0, 90, 180, 270, 360 这几个值，
    并进行角度转换：270->90, 90->270, 360->0
    """
    possible_angles = [0, 90, 180, 270, 360]
    normalized_angle = raw_angle % 360
    closest_angle = min(possible_angles, key=lambda x: abs(x - normalized_angle))
    # 角度转换映射
    angle_mapping = {
        270: 90,
        90: 270,
        360: 0
    }
    return angle_mapping.get(closest_angle, closest_angle)



def horizontal_merge(
    lines_data,
    max_horizontal_gap=10,
    max_y_diff=5,
    check_font_size=True,
    check_font_name=True,
    check_font_color=True,
    bold_max_horizontal_gap=20  # ← 新增：粗体文本的自定义合并间距
):
    """
    水平方向合并：保留原始 PDF 顺序，判断同一水平行、间距小，
    且可选同一字体大小/名称/颜色时合并。
    新增：合并后统计 total_bold_chars / total_nonbold_chars，判断整行是否为粗体。
    新增：如果当前行或上一行是粗体，则使用自定义的 bold_max_horizontal_gap 作为最大水平间距。
    【改动】：在合并时，合并子行的 font_names 字段，避免只保留一个。
    """
    merged = []
    for line in lines_data:
        x0, y0, x1, y1 = line["line_bbox"]
        inserted = False

        if merged:
            prev_line = merged[-1]
            px0, py0, px1, py1 = prev_line["line_bbox"]

            # 基础条件
            same_block = (line["block_index"] == prev_line["block_index"])
            same_font_size_flag = (line["font_size"] == prev_line["font_size"])
            same_font_name_flag = (line["font_name"] == prev_line["font_name"])

            # 颜色差判断
            color_diff_val = 0
            if (line["font_color"] is not None) and (prev_line["font_color"] is not None):
                color_diff_val = abs(line["font_color"] - prev_line["font_color"])
            same_font_color_flag = (color_diff_val <= 500000)

            # 根据开关决定是否要求它们一致
            if not check_font_size:
                same_font_size_flag = True
            if not check_font_name:
                same_font_name_flag = True
            if not check_font_color:
                same_font_color_flag = True

            # 若两行的字体大小有 None，则先做一下简单兜底处理
            curr_font_size = line["font_size"] if line["font_size"] else 10
            prev_font_size = prev_line["font_size"] if prev_line["font_size"] else 10

            # 如果当前行或上一个行是粗体，则使用 bold_max_horizontal_gap
            if line["font_bold"] and prev_line["font_bold"]:
                effective_max_gap = (curr_font_size + prev_font_size)
            else:
                # 原逻辑：动态计算最大水平间距
                effective_max_gap = (curr_font_size + prev_font_size) / 1.7

            # 1) 打印或调试用
            # print('最大x间距(根据是否粗体调节后)', effective_max_gap, line['text'])

            # 2) 将 max_y_diff 改为该均值的一半（用户原逻辑）
            #   这里也可以区分是否是粗体做进一步的调节，不过暂时先不分
            max_y_diff = effective_max_gap / 2.0

            # 判断是否在同一水平行
            y0_diff = abs(y0 - py0)
            y1_diff = abs(y1 - py1)
            same_horizontal_line = (y0_diff < max_y_diff and y1_diff < max_y_diff)

            # 判断水平间距是否足够小
            horizontal_gap = x0 - px1
            close_enough = (0 <= horizontal_gap < effective_max_gap)

            # 如果满足合并条件，则合并
            if (
                same_block
                and same_font_size_flag
                and same_font_name_flag
                and same_font_color_flag
                and same_horizontal_line
                and close_enough
            ):
                # 合并文本
                prev_line["text"] = prev_line["text"].rstrip() + " " + line["text"].lstrip()
                # 更新 bbox
                new_x0 = min(px0, x0)
                new_y0 = min(py0, y0)
                new_x1 = max(px1, x1)
                new_y1 = max(py1, y1)
                prev_line["line_bbox"] = (new_x0, new_y0, new_x1, new_y1)

                # 合并粗体/非粗体字符数
                prev_line["total_bold_chars"] += line["total_bold_chars"]
                prev_line["total_nonbold_chars"] += line["total_nonbold_chars"]

                # 更新 font_bold
                if prev_line["total_bold_chars"] > prev_line["total_nonbold_chars"]:
                    prev_line["font_bold"] = True
                else:
                    prev_line["font_bold"] = False

                # 合并字体名称（核心改动）
                prev_line["font_names"].extend(line["font_names"])
                # 去重
                prev_line["font_names"] = list(set(prev_line["font_names"]))

                inserted = True

        if not inserted:
            merged.append(line)

    return merged


def merge_lines(lines_data, check_font_size=True, check_font_name=True, check_font_color=True):
    """
    垂直方向合并示例，包含多段合并逻辑(1,2,3) + "中间合并豁免"逻辑。
    新增：颜色差值判断，可选启用；以及合并后统计 total_bold_chars / total_nonbold_chars 判断整行粗体。
    新增：condition_4：若上一行 bbox 可以包裹当前行 bbox（含2像素容差），则合并。
• condition_1 (中间豁免合并)：若当前行在上一行的 bbox 范围内（x0≥px0+margin_in_middle，x1≤px1-margin_in_middle 等），且字体大小、颜色等基本一致，则认为是同段落被拆分的行。
• condition_2 (新逻辑合并)：对上一行右边界和当前行 x1 等进行限制，强调“上一行右边界明显包住当前行的宽度”，可理解为同一行拆成多段。
• condition_3 (老逻辑合并)：只要块号相同、Y 轴距离足够小、字体等一致就合并；里面还包含了对行宽差别 (width_diff) 的一些自定义判断、缩进处理等。
• condition_4 (包裹合并)：如果上一行能在四个方向上包裹当前行（含 2 像素容差），则直接把当前行合并进上一行。
    【改动】：在合并时，合并子行的 font_names 字段，避免只保留一个。
    """

    merged = []
    # 横向距离阈值(非中间豁免时要满足此判断)
    max_x_distance = 80
    # “行在上一行中间”的左右边界余量阈值
    margin_in_middle = 5

    for idx_line, line in enumerate(lines_data, start=1):
        # 每行初始缩进量
        line["indent"] = 0
        x0, y0, x1, y1 = line["line_bbox"]
        current_width = (x1 - x0)

        if not merged:
            merged.append(line)
            continue

        prev_line = merged[-1]
        px0, py0, px1, py1 = prev_line["line_bbox"]
        prev_width = (px1 - px0)

        # 基础属性判断
        same_block = (line["block_index"] == prev_line["block_index"])
        same_font_size_flag = (line["font_size"] == prev_line["font_size"])
        same_font_name_flag = (line["font_name"] == prev_line["font_name"])

        # 颜色差
        color_diff_val = 0
        if line["font_color"] is not None and prev_line["font_color"] is not None:
            color_diff_val = abs(line["font_color"] - prev_line["font_color"])
        same_font_color_flag = (color_diff_val <= 500000)

        # 根据 check_xxx 决定是否严格要求它们一致
        if not check_font_size:
            same_font_size_flag = True
        if not check_font_name:
            same_font_name_flag = True
        if not check_font_color:
            same_font_color_flag = True

        curr_font_size = line["font_size"] if line["font_size"] else 10
        prev_font_size = prev_line["font_size"] if prev_line["font_size"] else 10

        # 1) 将 max_horizontal_gap 改为相邻行字体大小的均值
        max_horizontal_gap = (curr_font_size + prev_font_size) / 2.0
        # 2) 将 max_y_diff 改为该均值的一半
        margin_in_middle = max_horizontal_gap / 1.5
        max_x_distance = max_horizontal_gap * 8

        # Y 轴距离判断
        y_distance = (y0 - py1)
        y_distance_small = (abs(y_distance) < margin_in_middle)

        # X 轴距离判断
        horizontal_distance = abs(x0 - px0)
        x_distance_small = (horizontal_distance < max_x_distance)

        # condition_1: “中间合并豁免”
        condition_1 = (
            same_block
            and same_font_size_flag
            and same_font_name_flag
            and same_font_color_flag
            and y_distance_small
            and (x0 >= px0 + margin_in_middle)
            and (x1 <= px1 - margin_in_middle)
        )

        # condition_2：新逻辑合并
        condition_2 = (
            same_block
            and y_distance_small
            and x_distance_small
            and (px1 >= x1)
            and (abs(px0 - x0) < margin_in_middle / 2.5)
        )

        # condition_3：老逻辑合并
        condition_3 = (
            same_block
            and y_distance_small
            and same_font_size_flag  # 可选
            and same_font_name_flag
            and same_font_color_flag
            and x_distance_small
        )

        # 【新增】 condition_4: “包裹合并”逻辑
        # 若上一行的 bbox 可以包裹当前行的 bbox（在容差2像素内）
        tolerance = 4.0
        condition_4 = (
                same_block
                and (x0 >= px0 - tolerance)
                and (y0 >= py0 - tolerance)
                and (x1 <= px1 + tolerance)
                and (y1 <= py1 + tolerance)
        )
        # print(f"[merge_lines_debug] ----------")
        # print(f" 当前行 idx_line = {idx_line}")
        # print(f" 上一行 bbox = ({px0:.2f}, {py0:.2f}, {px1:.2f}, {py1:.2f}), prev_width = {prev_width:.2f}")
        # print(f" 当前行 bbox = ({x0:.2f}, {y0:.2f}, {x1:.2f}, {y1:.2f}), current_width = {current_width:.2f}")
        # print(f" same_block = {same_block}, same_font_size = {same_font_size_flag}, same_font_name = {same_font_name_flag}")
        # print(f" same_font_color = {same_font_color_flag}")
        # print(f" y_distance = {y_distance:.2f}, y_distance_small = {y_distance_small}")
        # print(f" x_distance = {horizontal_distance:.2f}, x_distance_small = {x_distance_small}")
        # print(f" condition_1 = {condition_1}")
        # print(f" condition_2 = {condition_2}")
        # print(f" condition_3 = {condition_3}")
        # print(f" condition_4 (包裹合并) = {condition_4}")

        # (1) condition_1 -> 中间豁免合并
        if condition_1:
            # print(f"[merge_lines_debug] -> 命中 condition_1 (中间豁免合并)，进行合并")
            merged[-1]["text"] = prev_line["text"].rstrip() + " " + line["text"].lstrip()
            new_x0 = min(px0, x0)
            new_y0 = min(py0, y0)
            new_x1 = max(px1, x1)
            new_y1 = max(py1, y1)
            merged[-1]["line_bbox"] = (new_x0, new_y0, new_x1, new_y1)
            # 合并粗体/非粗体字符数
            merged[-1]["total_bold_chars"] += line["total_bold_chars"]
            merged[-1]["total_nonbold_chars"] += line["total_nonbold_chars"]
            # 判断最终粗体
            if merged[-1]["total_bold_chars"] > merged[-1]["total_nonbold_chars"]:
                merged[-1]["font_bold"] = True
            else:
                merged[-1]["font_bold"] = False
            # 合并所有字体名称
            merged[-1]["font_names"].extend(line["font_names"])
            merged[-1]["font_names"] = list(set(merged[-1]["font_names"]))

            if line["font_size"] is not None and line["font_size"] > margin_in_middle * 2:
                merged[-1]["type"] = "title"

            continue

        # (2) condition_2 -> 新逻辑合并
        elif condition_2:
            # print(f"[merge_lines_debug] -> 命中 condition_2 (new_merge_condition)，进行合并")
            merged[-1]["text"] = prev_line["text"].rstrip() + " " + line["text"].lstrip()
            new_x0 = min(px0, x0)
            new_y0 = min(py0, y0)
            new_x1 = max(px1, x1)
            new_y1 = max(py1, y1)
            merged[-1]["line_bbox"] = (new_x0, new_y0, new_x1, new_y1)
            # 合并粗体/非粗体字符数
            merged[-1]["total_bold_chars"] += line["total_bold_chars"]
            merged[-1]["total_nonbold_chars"] += line["total_nonbold_chars"]
            # 判断最终粗体
            if merged[-1]["total_bold_chars"] > merged[-1]["total_nonbold_chars"]:
                merged[-1]["font_bold"] = True
            else:
                merged[-1]["font_bold"] = False
            # 合并所有字体名称
            merged[-1]["font_names"].extend(line["font_names"])
            merged[-1]["font_names"] = list(set(merged[-1]["font_names"]))
            continue

        # (3) condition_3 -> 老逻辑合并
        elif condition_3:
            # print("[merge_lines_debug] -> 命中 condition_3 (老逻辑合并)")
            # 先判断：若下一行 (x1 - px1) > max_x_distance，则不合并
            if (x1 - px1) > max_x_distance:
                # print("[merge_lines_debug] -> 下一行 x1 比上一行 x1 超出阈值，不合并")
                merged.append(line)
                continue

            width_diff = abs(current_width - prev_width)
            # print(f"[merge_lines_debug] -> width_diff = {width_diff:.2f}")

            if width_diff <= margin_in_middle / 2.5:
                # 直接合并
                # print("[merge_lines_debug] -> width_diff 较小，进行合并")
                merged_text = prev_line["text"].rstrip() + " " + line["text"].lstrip()
                prev_line["text"] = merged_text
                new_x0 = min(px0, x0)
                new_y0 = min(py0, y0)
                new_x1 = max(px1, x1)
                new_y1 = max(py1, y1)
                prev_line["line_bbox"] = (new_x0, new_y0, new_x1, new_y1)
                # 合并粗体/非粗体字符数
                prev_line["total_bold_chars"] += line["total_bold_chars"]
                prev_line["total_nonbold_chars"] += line["total_nonbold_chars"]
                # 判断最终粗体
                if prev_line["total_bold_chars"] > prev_line["total_nonbold_chars"]:
                    prev_line["font_bold"] = True
                else:
                    prev_line["font_bold"] = False
                # 合并所有字体名称
                prev_line["font_names"].extend(line["font_names"])
                prev_line["font_names"] = list(set(prev_line["font_names"]))
                continue
            else:
                # 宽度差 > 2 时的自定义逻辑
                # (1) 若上一行更窄 + px0 > x0，则记录缩进并合并
                if (prev_width < current_width) and (px0 > x0):
                    indent_val = abs(px0 - x0)
                    # print(f"[merge_lines_debug] -> (宽度差>2) + (上一行更窄 + x0比较)，记录缩进={indent_val:.2f} 并合并")
                    merged[-1]["indent"] = indent_val
                    merged_text = prev_line["text"].rstrip() + " " + line["text"].lstrip()
                    prev_line["text"] = merged_text
                    new_x0 = min(px0, x0)
                    new_y0 = min(py0, y0)
                    new_x1 = max(px1, x1)
                    new_y1 = max(py1, y1)
                    prev_line["line_bbox"] = (new_x0, new_y0, new_x1, new_y1)
                    # 合并粗体/非粗体字符数
                    prev_line["total_bold_chars"] += line["total_bold_chars"]
                    prev_line["total_nonbold_chars"] += line["total_nonbold_chars"]
                    # 判断最终粗体
                    if prev_line["total_bold_chars"] > prev_line["total_nonbold_chars"]:
                        prev_line["font_bold"] = True
                    else:
                        prev_line["font_bold"] = False
                    # 合并所有字体名称
                    prev_line["font_names"].extend(line["font_names"])
                    prev_line["font_names"] = list(set(prev_line["font_names"]))
                    continue
                # (2) 若当前行更窄 + 当前行x0>=上一行x0+2，则不合并
                elif (current_width < prev_width) and (x0 >= px0 + 2):
                    # print("[merge_lines_debug] -> (宽度差>2) + (当前行更窄)，不合并")
                    merged.append(line)
                    continue
                # (3) 其它情况沿用以往做法
                else:
                    # print("[merge_lines_debug] -> (宽度差>2) 但不满足(1)/(2)新条件，仍按老逻辑合并")
                    if prev_width < current_width:
                        indent_val = abs(px0 - x0)
                        # print(f"[merge_lines_debug] -> 老逻辑记录缩进 indent = {indent_val:.2f}")
                        merged[-1]["indent"] = indent_val
                    merged_text = prev_line["text"].rstrip() + " " + line["text"].lstrip()
                    prev_line["text"] = merged_text
                    new_x0 = min(px0, x0)
                    new_y0 = min(py0, y0)
                    new_x1 = max(px1, x1)
                    new_y1 = max(py1, y1)
                    prev_line["line_bbox"] = (new_x0, new_y0, new_x1, new_y1)
                    # 合并粗体/非粗体字符数
                    prev_line["total_bold_chars"] += line["total_bold_chars"]
                    prev_line["total_nonbold_chars"] += line["total_nonbold_chars"]
                    # 判断最终粗体
                    if prev_line["total_bold_chars"] > prev_line["total_nonbold_chars"]:
                        prev_line["font_bold"] = True
                    else:
                        prev_line["font_bold"] = False
                    # 合并所有字体名称
                    prev_line["font_names"].extend(line["font_names"])
                    prev_line["font_names"] = list(set(prev_line["font_names"]))
                    continue

        # (4) condition_4 -> 被上一行包裹的合并（新逻辑）
        elif condition_4:
            # print("[merge_lines_debug] -> 命中 condition_4 (行被上一行包裹)，进行合并")
            merged[-1]["text"] = prev_line["text"].rstrip() + " " + line["text"].lstrip()
            new_x0 = min(px0, x0)
            new_y0 = min(py0, y0)
            new_x1 = max(px1, x1)
            new_y1 = max(py1, y1)
            merged[-1]["line_bbox"] = (new_x0, new_y0, new_x1, new_y1)
            # 合并粗体/非粗体字符数
            merged[-1]["total_bold_chars"] += line["total_bold_chars"]
            merged[-1]["total_nonbold_chars"] += line["total_nonbold_chars"]
            # 判断最终粗体
            if merged[-1]["total_bold_chars"] > merged[-1]["total_nonbold_chars"]:
                merged[-1]["font_bold"] = True
            else:
                merged[-1]["font_bold"] = False
            # 合并所有字体名称
            merged[-1]["font_names"].extend(line["font_names"])
            merged[-1]["font_names"] = list(set(merged[-1]["font_names"]))
            continue

        else:
            # print("[merge_lines_debug] -> 不符合任何合并条件，直接append")
            merged.append(line)

    return merged


def is_math(font_info_list, text_len, text,font_size):
    """
    判断文本是否为数学公式(或长度太短)，如果是，则排除(标记为 math)。
    """

    # 若行整体长度 < 50，检查字体集合与数学字体集合是否有交集
    text_length_nospaces = len(text.replace(" ", ""))
    if text_length_nospaces < font_size * 3:
        font_set = set(font_info_list)
        if font_set & MATH_FONTS_SET:
            # print('math,',text)
            return True

    # if text_len <2:
    #     return True
    # 如果长度很短，且全是数字/标点，这里原逻辑是将其视为数字类信息
    # 但如果完全想区分“纯数字” vs “公式”，可自行调整。
    if text_len < font_size:
        text = text.strip()
        for ch in text:
            cat = unicodedata.category(ch)  # 'Nd' -> 数字； 'P' -> 标点
            if not (cat == 'Nd' or cat.startswith('P')):
                return False
        # 如果走到这里，说明短文本几乎全是数字或标点，原逻辑中打印“纯数字”并返回 True
        # print(text, '纯数字')
        return True



    return False


def merge_adjacent_math_lines(lines):
    """
    对相邻行进行多次合并(只需一次遍历即可完成)：
        1) 若两行都为 math，且相邻行 x / y 距离足够小，则合并。
        2) 若两行中有且仅有一行是 math，另一行长度非常短(小于一定阈值)，且 x / y 距离足够小，则先将那行也标记为 math，再合并。

    其中 x_distance / y_distance 的计算方式为：
        x_distance = min(|px0 - cx1|, |cx0 - px1|)
        y_distance = min(|py0 - cy1|, |cy0 - py1|)

    注：如果 lines 已按阅读顺序排好(从上至下、从左至右)，则在一次扫描中可以将
        所有可以相邻合并的 math 行都合并完成，而不会漏掉“第一次合并后才新形成
        邻接关系”的情况。算法整体复杂度约为 O(N)。
    """

    if not lines:
        return []

    def get_font_size(line):
        # 若行的 font_size 为 None，则简单兜底为 10
        return line["font_size"] if line["font_size"] else 10

    def can_merge(prev_line, curr_line):
        """
        判断是否能将 curr_line 合并到 prev_line。
        如果返回 (True, 'BOTH_MATH'/'ONE_MATH_PREV'/'ONE_MATH_CURR'),
        表示可合并并说明是哪种类型；若返回 (False, None) 则不能合并。
        """
        px0, py0, px1, py1 = prev_line["line_bbox"]
        cx0, cy0, cx1, cy1 = curr_line["line_bbox"]

        # x / y 方向上的最近距离
        x_distance = min(abs(px0 - cx1), abs(cx0 - px1))
        y_distance = min(abs(py0 - cy1), abs(cy0 - py1))

        # 也可以考虑检测部分重叠
        x_distance_overlap = min(abs(px0 - cx0), abs(cx1 - px1))

        prev_is_math = (prev_line["type"] == "math")
        curr_is_math = (curr_line["type"] == "math")
        prev_len = prev_line["total_bold_chars"] + prev_line["total_nonbold_chars"]
        curr_len = curr_line["total_bold_chars"] + curr_line["total_nonbold_chars"]

        fs_p = get_font_size(prev_line)
        fs_c = get_font_size(curr_line)
        max_horizontal_gap = (fs_p + fs_c) / 2.0  # 动态阈值

        # 条件 1：两行都为 math，并且距离较小
        cond_math_both = (
            prev_is_math
            and curr_is_math
            and (
                (x_distance < 5 * max_horizontal_gap and y_distance < 3 * max_horizontal_gap)
                or (x_distance_overlap < 5 * max_horizontal_gap and y_distance < 3 * max_horizontal_gap)
            )
        )

        # 条件 2：只有一行是 math，且另一行非常短; 距离也小
        cond_one_math_prev = (
            prev_is_math
            and not curr_is_math
            and (curr_len < max_horizontal_gap)
            and (x_distance < 2 * max_horizontal_gap)
            and (y_distance < 1.5 * max_horizontal_gap)
        )
        cond_one_math_curr = (
            not prev_is_math
            and curr_is_math
            and (prev_len < max_horizontal_gap)
            and (x_distance < 2 * max_horizontal_gap)
            and (y_distance < 1.5 * max_horizontal_gap)
        )

        if cond_math_both:

            return (True, "BOTH_MATH")
        elif cond_one_math_prev:
            return (True, "ONE_MATH_PREV")
        elif cond_one_math_curr:
            return (True, "ONE_MATH_CURR")
        else:
            return (False, None)

    def do_merge(prev_line, curr_line, merge_type):
        """
        将 curr_line 合并到 prev_line，并根据 merge_type 做必要的类型标记。
        返回合并后的行(即 prev_line)。注意这是原地修改 prev_line。
        """
        # 若是 "ONE_MATH_CURR"，说明 curr_line 是 math，prev_line 要标记成 math
        if merge_type == "ONE_MATH_CURR":
            prev_line["type"] = "math"
        # 若是 "ONE_MATH_PREV"，说明 prev_line 是 math，要把 curr_line 标记为 math
        elif merge_type == "ONE_MATH_PREV":
            curr_line["type"] = "math"
        # "BOTH_MATH" 不用特别改标记

        # 合并文本与 bbox
        prev_line["text"] = prev_line["text"].rstrip() + " " + curr_line["text"].lstrip()
        px0, py0, px1, py1 = prev_line["line_bbox"]
        cx0, cy0, cx1, cy1 = curr_line["line_bbox"]
        prev_line["line_bbox"] = (
            min(px0, cx0),
            min(py0, cy0),
            max(px1, cx1),
            max(py1, cy1),
        )

        # 合并字体、字数
        prev_line["font_names"] = list(set(prev_line["font_names"] + curr_line["font_names"]))
        prev_line["total_bold_chars"] += curr_line["total_bold_chars"]
        prev_line["total_nonbold_chars"] += curr_line["total_nonbold_chars"]

        return prev_line

    new_lines = []
    for curr_line in lines:
        # 尝试和栈顶行合并, 若可以则合并再继续看是否能与更早的行合并(链式)
        while new_lines:
            can_merge_flag, merge_type = can_merge(new_lines[-1], curr_line)
            if can_merge_flag:
                # 弹出栈顶行, 和 curr_line 合并
                merged = do_merge(new_lines.pop(), curr_line, merge_type)
                # 合并后要让 merged 作为“新的 curr_line”再尝试和更早的行合并
                curr_line = merged
            else:
                # 无法和栈顶合并, 则停止
                break

        # 最后把 curr_line (可能是合并后的结果) 压入栈
        new_lines.append(curr_line)

    return new_lines



def get_new_blocks(page):
    """
    从指定 PDF 的某页提取文本行(blocks->lines->spans)，
    做基础的过滤和 bbox 合并后，得到行数据 lines_data。
    然后：
      1) horizontal_merge(): 水平合并
      2) merge_lines(): 垂直合并
      3) 基于“行号 + 块号 + 行类型 + 字符长度”等信息构建临时数据结构，判断整块是否可疑
      4) 若可疑（小于某字符数且含 math 行）则整块标记为 math
      5) 最后合并相邻 math 行
      6) 打印(或返回)结果
    """

    try:
        page = page


        blocks = page.get_text("dict")["blocks"]
        lines_data = []

        # ============= 读取并初步整理行信息 =============
        for i, block in enumerate(blocks, start=1):
            if 'lines' not in block:
                continue
            for line in block["lines"]:
                spans = line.get("spans", [])
                if not spans:
                    continue

                filtered_spans = spans  # 此处可插入自定义过滤逻辑
                if not filtered_spans:
                    continue

                # 1) 计算这一行的 bbox（合并 filtered_spans 的 bbox）
                x0_list, y0_list, x1_list, y1_list = [], [], [], []
                for span in filtered_spans:
                    if "bbox" in span:
                        sbbox = span["bbox"]
                        x0_list.append(sbbox[0])
                        y0_list.append(sbbox[1])
                        x1_list.append(sbbox[2])
                        y1_list.append(sbbox[3])

                if x0_list and y0_list and x1_list and y1_list:
                    new_line_bbox = (
                        min(x0_list), min(y0_list),
                        max(x1_list), max(y1_list),
                    )
                else:
                    new_line_bbox = line["bbox"]

                # 2) 拼接文本，并收集字体等信息
                full_text = ""
                font_sizes = set()
                colors = set()
                bold_flags = []
                longest_span_length = 0
                longest_span_font = None
                font_names_set = set()

                for span in filtered_spans:
                    span_text = span["text"]
                    full_text += span_text
                    font_sizes.add(span["size"])
                    colors.add(span["color"])

                    this_font_name = span.get("font", "")
                    font_names_set.add(this_font_name)

                    # 判断是否加粗
                    is_bold = span.get("face", {}).get("bold", False)
                    if not is_bold:
                        # 额外判断关键字
                        bold_keywords = ["bold", "cmbx", "heavy", "demi"]
                        lower_font_name = this_font_name.lower()
                        for kw in bold_keywords:
                            if kw in lower_font_name:
                                is_bold = True
                                break
                    bold_flags.append(is_bold)

                    # 统计 span 的有效字符长度(去除空格)
                    stripped_span_text = span_text.strip()
                    span_len = len(stripped_span_text)
                    if span_len > longest_span_length:
                        longest_span_length = span_len
                        longest_span_font = this_font_name

                line_is_bold = any(bold_flags)
                stripped_text = full_text.strip()
                if not stripped_text:
                    continue


                # 3) 若行首有“•”，则去掉并向右偏移
                if stripped_text.startswith("•"):
                    stripped_text = stripped_text[1:].lstrip()
                    new_line_bbox = (
                        new_line_bbox[0] + 10,
                        new_line_bbox[1],
                        new_line_bbox[2],
                        new_line_bbox[3],
                    )
                    full_text = stripped_text

                # 4) 计算行的旋转角度(吸附至0/90/180/270/360)
                raw_angle = math.degrees(
                    math.atan2(
                        line.get("dir", [1.0, 0.0])[1],
                        line.get("dir", [1.0, 0.0])[0]
                    )
                )
                angle = snap_angle_func(raw_angle)

                # 5) 使用最长 span 的字体名称作为行的 font_name（代表字体）
                chosen_font_name = longest_span_font if longest_span_font else None
                line_len = len(full_text)

                # 初始化该行的粗体/非粗体字符累加
                if line_is_bold:
                    tb = line_len  # total_bold_chars
                    tnb = 0
                else:
                    tb = 0
                    tnb = line_len

                line_data = {
                    "block_index": i,
                    "line_bbox": new_line_bbox,
                    "text": full_text,
                    "font_size": (list(font_sizes)[0] if font_sizes else None),
                    "font_color": (list(colors)[0] if colors else None),
                    "font_name": chosen_font_name,    # 仅代表字体名称
                    "font_names": list(font_names_set),  # 全部子span字体集合
                    "rotation_angle": angle,
                    "type": "plain_text",             # 初始行类型
                    "font_bold": line_is_bold,
                    "indent": 0,
                    "total_bold_chars": tb,
                    "total_nonbold_chars": tnb
                }
                lines_data.append(line_data)



        if not lines_data:
            print("该页面没有提取到任何文本行")
            return

        # ============= (1) 水平合并 =============
        merged_horizontally = horizontal_merge(
            lines_data,
            max_horizontal_gap=20,
            max_y_diff=5,
            check_font_size=True,
            check_font_name=True,
            check_font_color=True
        )

        # ============= (2) 垂直合并 =============
        merged_final = merge_lines(
            merged_horizontally,
            check_font_size=True,
            check_font_name=True,
            check_font_color=True
        )

        # ============= (3) 基于合并后行信息，构建临时数据结构 =============
        #    存储块号 -> [ (行在 merged_final 列表中的索引, 字符长度, 行类型) ... ]，
        #    并统计块内总字符数。
        temp_block_dict = defaultdict(lambda: {
            'lines': [],       # [(merged_final_idx, line_type, text_len), ...]
            'total_chars': 0   # 整个 block 的字符串长度总和
        })

        for idx, line_info in enumerate(merged_final):
            # 计算该行字符长度
            text_len = line_info['total_bold_chars'] + line_info['total_nonbold_chars']
            # 判断是否是 math（行类型先设置，这里只是初步）
            final_text = line_info['text'] or ''

            if final_text and is_math(line_info['font_names'], text_len, final_text,line_info['font_size']):
                line_info['type'] = 'math'
            block_idx = line_info['block_index']
            temp_block_dict[block_idx]['lines'].append(
                (idx, line_info['type'], text_len)
            )
            temp_block_dict[block_idx]['total_chars'] += text_len

        # ============= (4) 根据块信息，若块内总字符数 < 50 且含有一行 math，则全块标记为 math =============
        for b_idx, block_data in temp_block_dict.items():
            total_chars = block_data['total_chars']
            lines_in_block = block_data['lines']
            # 判断该 block 是否含 math
            has_math_in_block = any(ln_type == 'math' for (_, ln_type, _) in lines_in_block)
            if (total_chars < 30) and has_math_in_block:
                # 将该 block 下所有行都标记为 math
                for (merged_idx, _, _) in lines_in_block:
                    merged_final[merged_idx]['type'] = 'math'

        # ============= (5) 对相邻 math 行进行二次合并 =============
        merged_final = merge_adjacent_math_lines(merged_final)

        # ============= (6) 打印结果并构造返回值 =============
        new_blocks = []
        for idx, line_info in enumerate(merged_final, start=1):
            # print(f"行 {idx}:")
            # print(f" 所属块序号(block_index): {line_info['block_index']}")
            # print(f" 行坐标(line_bbox): {line_info['line_bbox']}")
            # print(f" 文本(text): {line_info['text']}")
            # print(f" 字体大小(font_size): {line_info['font_size']}")
            # print(f" 字体颜色(font_color): {line_info['font_color']}")
            # print(f" 代表字体名称(font_name): {line_info['font_name']}")
            # print(f" 所有字体名称(all_font_names): {line_info['font_names']}")
            # print(f" 旋转角度(rotation_angle): {line_info['rotation_angle']}°")
            # print(f" 字体加粗(font_bold): {line_info['font_bold']}")
            # print(f" 缩进(indent): {line_info['indent']}")
            # print(f" total_bold_chars = {line_info['total_bold_chars']}, total_nonbold_chars = {line_info['total_nonbold_chars']}")
            # print(f" 行类型(type): {line_info['type']}")
            # print("-" * 50)

            new_blocks.append([
                line_info['text'],
                tuple(line_info['line_bbox']),
                line_info['type'],
                line_info['rotation_angle'],
                line_info['font_color'],
                line_info['indent'],
                line_info['font_bold'],
                line_info['font_size']
            ])

        return new_blocks

    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    b = datetime.datetime.now()
    pdf_path = "g2.pdf"  # 换成你的 PDF 文件路径
    page_number = 1   # 换成想处理的页码
    z = get_new_blocks(pdf_path, page_number)
    print("最终返回的 new_blocks:", z)
    e = datetime.datetime.now()
    elapsed_time = (e - b).total_seconds()
    print(f"运行时间: {elapsed_time} 秒")
