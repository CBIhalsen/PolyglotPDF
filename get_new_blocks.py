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
    "Neo Euler", 'MTMI', 'MTSYN', 'TimesNewRomanPSMT'
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
    check_font_size=False,
    check_font_name=False,
    check_font_color=False,
    bold_max_horizontal_gap=20
):
    """
    水平方向合并（光标推进式），只对相邻两行递推判断能否合并，合并后光标不移动。
    """
    if not lines_data:
        return []

    merged = []
    i = 0
    n = len(lines_data)
    while i < n:
        line = lines_data[i]
        if not merged:
            merged.append(line)
            i += 1
            continue

        prev_line = merged[-1]
        x0, y0, x1, y1 = line["line_bbox"]
        px0, py0, px1, py1 = prev_line["line_bbox"]
        curr_font_size = line["font_size"] if line["font_size"] else 10
        prev_font_size = prev_line["font_size"] if prev_line["font_size"] else 10
        avg_font_size = (curr_font_size+prev_font_size)/2
        # (1) 如果 x、y 轴范围都有交集，就直接合并
        overlap_y = (y0 <= py1) and (py0 <= y1) and (abs(y0-py1)>avg_font_size/5)
        overlap_x = (x0 <= px1) and (px0 <= x1)
        merged_this_round = False

        if overlap_x and overlap_y:
            prev_line["text"] = prev_line["text"].rstrip() + " " + line["text"].lstrip()

            new_x0 = min(px0, x0)
            new_y0 = min(py0, y0)
            new_x1 = max(px1, x1)
            new_y1 = max(py1, y1)
            prev_line["line_bbox"] = (new_x0, new_y0, new_x1, new_y1)
            prev_line["total_bold_chars"] += line["total_bold_chars"]
            prev_line["total_nonbold_chars"] += line["total_nonbold_chars"]
            prev_line["font_bold"] = prev_line["total_bold_chars"] > prev_line["total_nonbold_chars"]
            prev_line["font_names"].extend(line["font_names"])
            prev_line["font_names"] = list(set(prev_line["font_names"]))
            merged_this_round = True
        else:
            # (2) 细化合并条件
            same_block = (line["block_index"] == prev_line["block_index"])
            same_font_size_flag = (line["font_size"] == prev_line["font_size"])
            same_font_name_flag = (line["font_name"] == prev_line["font_name"])

            color_diff_val = 0
            if line["font_color"] is not None and prev_line["font_color"] is not None:
                color_diff_val = abs(line["font_color"] - prev_line["font_color"])
            same_font_color_flag = (color_diff_val <= 50)

            # 根据开关放宽判断
            if not check_font_size:
                same_font_size_flag = True
            if not check_font_name:
                same_font_name_flag = True
            if not check_font_color:
                same_font_color_flag = True



            if line["font_bold"] and prev_line["font_bold"]:
                effective_max_gap = avg_font_size
            else:
                effective_max_gap = avg_font_size

            # y轴重叠判据

            same_horizontal_line = abs(py1-y1)<avg_font_size/5   and abs(py0-y0)<avg_font_size/5

            horizontal_gap = x0 - px1
            close_enough = (0 <= horizontal_gap < effective_max_gap)

            if (same_block and same_font_size_flag and same_font_name_flag
                and same_font_color_flag and same_horizontal_line and close_enough
            ):
                prev_line["text"] = (
                    prev_line["text"].rstrip() + " " + line["text"].lstrip()
                )

                new_x0 = min(px0, x0)
                new_y0 = min(py0, y0)
                new_x1 = max(px1, x1)
                new_y1 = max(py1, y1)
                prev_line["line_bbox"] = (new_x0, new_y0, new_x1, new_y1)
                prev_line["total_bold_chars"] += line["total_bold_chars"]
                prev_line["total_nonbold_chars"] += line["total_nonbold_chars"]
                prev_line["font_bold"] = prev_line["total_bold_chars"] > prev_line["total_nonbold_chars"]
                prev_line["font_names"].extend(line["font_names"])
                prev_line["font_names"] = list(set(prev_line["font_names"]))
                merged_this_round = True

        if merged_this_round:
            # 合并成功，继续用当前 prev_line 和下一行比较
            i += 1
            continue
        else:
            # 没合并，推进光标，当前行直接进 merged
            merged.append(line)
            i += 1

    # 打印合并后结果
    # for idx, line in enumerate(merged, 1):
    #     text = line["text"]
    #     bbox = line["line_bbox"]
    #     print(f"水平行 {idx}: text = {text!r}, bbox = {bbox}")

    return merged

def merge_lines(lines_data, check_font_size=False, check_font_name=True, check_font_color=True,check_same_block=True ):
    """
    垂直方向合并函数（合并后继续检查当前位置，不全量遍历回头）
    支持四种合并逻辑 condition_1 ~ condition_4
# condition_1: “中间合并豁免”或“包裹型合并（对称）”
# 说明：当前行左右都被上一行包住，中间至少留 margin_in_middle 空隙，
# 并且左右包裹“对称性好”（左右两端冗余的差值不能太大），
# 常见于公式换行、PDF多栏切分等情形，防止“孤行”被误合并进大段。
condition_1 = (
    same_block and same_font_size_flag and same_font_name_flag and same_font_color_flag
    and y_distance_small
    and (x0 >= px0 + margin_in_middle) and (x1 <= px1 - margin_in_middle)
    and no_end_indent
    and abs(abs(x0-px0) - abs(x1-px1)) < max_horizontal_gap
)

# condition_2: “新逻辑合并”
# 说明：只要同块、竖直距离和水平距离都很近（左右对齐良好），并且没有末尾缩进，
# 主要针对“强制换行”、“正文伪换行”等排版产生的断行，适合合并正文连续段落。
condition_2 = (
    same_block and y_distance_small and x_distance_small
    and (abs(px0 - x0) < margin_in_middle) and no_end_indent
)

# condition_3: “经典合并”或“宽度近似合并”
# 说明：传统正文合并判据，要求同块、字体等属性接近、左右对齐好、宽度差值极小且无缩进。
# 主要用于正常正文行的自然换行处理。
condition_3 = (
    same_block and y_distance_small and same_font_size_flag and same_font_name_flag and same_font_color_flag
    and x_distance_small and no_end_indent
)

# condition_4: “BBox包裹合并（防漏）”
# 说明：上一行的bbox能完整包裹当前行（含一定容差 tolerance），常用于
# 脚注、特殊符号、页眉、页脚等特殊情况防止“残留孤行”被遗漏。
condition_4 = (
    same_block
    and (x0 >= px0 - tolerance) and (y0 >= py0 - tolerance)
    and (x1 <= px1 + tolerance) and (y1 <= py1 + tolerance)
    and no_end_indent
)

# condition_5: “二级新逻辑合并/容忍性补充”
# 说明：同块，竖直距离和水平距离都近，且左边界只比上一行多一点（不过多于2倍gap），
# 用于捕捉有轻微缩进或特殊段落起始的伪断行，防止漏合并。
condition_5 = (
    same_block and y_distance_small and x_distance_small
    and (px0 - x0) < max_horizontal_gap * 2
    and no_end_indent
)


    """

    merged = []
    i = 0
    n = len(lines_data)
    while i < n:
        line = lines_data[i]
        if not merged:
            merged.append(line)
            i += 1
            continue

        prev_line = merged[-1]
        x0, y0, x1, y1 = line["line_bbox"]
        px0, py0, px1, py1 = prev_line["line_bbox"]
        current_width = (x1 - x0)
        prev_width = (px1 - px0)
        prev_indent = prev_line['indent']

        # 判断同一块，增加是否启用的开关
        if check_same_block:
            same_block = (line["block_index"] == prev_line["block_index"])
        else:
            same_block = True  # 不检查时总为True
        # 无缩进
        no_end_indent = prev_line["end_indent"] == 0

        # 字体大小布尔标记
        if check_font_size:
            if line["font_size"] is not None and prev_line["font_size"] is not None:
                font_size_diff = abs(line["font_size"] - prev_line["font_size"])
                same_font_size_flag = (font_size_diff <= 0.6)
            else:
                same_font_size_flag = True
        else:
            same_font_size_flag = True
        # 字体名称布尔标记
        if check_font_name:
            same_font_name_flag = (line["font_name"] == prev_line["font_name"])
        else:
            same_font_name_flag = True
        # 字体颜色布尔标记
        color_diff_val = 0
        if line["font_color"] is not None and prev_line["font_color"] is not None:
            color_diff_val = abs(line["font_color"] - prev_line["font_color"])
        if check_font_color:
            same_font_color_flag = (color_diff_val <= 50)
        else:
            same_font_color_flag = True

        # 动态调整阈值
        curr_font_size = line["font_size"] if line["font_size"] else 10
        prev_font_size = prev_line["font_size"] if prev_line["font_size"] else 10
        max_horizontal_gap = (curr_font_size + prev_font_size) / 2.0
        margin_in_middle = max_horizontal_gap / 1.5
        max_x_distance = max_horizontal_gap * 8

        # Y 轴、X 轴距离
        y_distance = (y0 - py1)
        y_distance_small = (abs(y_distance) < max_horizontal_gap/1.3)
        horizontal_distance = abs(x0 - px0)
        x_distance_small = (horizontal_distance < max_x_distance)

        thorizontal_distance = abs(current_width - prev_width)


        # 判断水平/竖直重叠

        avg_font_size = (curr_font_size+prev_font_size)/2


        overlap_y = (y0 <= py1) and (py0 <= y1) and (abs(y0-py1)>avg_font_size/5)
        overlap_x = (x0 <= px1) and (px0 <= x1)

        # 合并条件
        # condition_1: “中间合并豁免”
        condition_1 = (
            same_block and same_font_size_flag and same_font_name_flag and same_font_color_flag
            and y_distance_small and (x0 >= px0 + margin_in_middle) and (x1 <= px1 - margin_in_middle)
            and no_end_indent and abs (abs(x0-px0) - abs(x1-px1)) < max_horizontal_gap
        )
        # condition_2: “新逻辑合并”
        condition_2 = (
            same_block and y_distance_small and x_distance_small
            and (abs(px0 - x0) < margin_in_middle) and no_end_indent and ((current_width - prev_width) < max_horizontal_gap*2)
        )
        # condition_3: “老逻辑合并”
        condition_3 = (
            same_block and y_distance_small and same_font_size_flag and same_font_name_flag and same_font_color_flag
            and x_distance_small and no_end_indent
        )
        # condition_4: “包裹合并”
        tolerance = max_horizontal_gap / 2
        condition_4 = (
            same_block and (x0 >= px0 - tolerance) and (y0 >= py0 - tolerance)
            and (x1 <= px1 + tolerance) and (y1 <= py1 + tolerance) and no_end_indent
        )
        # condition_5: “”
        condition_5 = (
            same_block and y_distance_small and x_distance_small
            and (px0-x0)< max_horizontal_gap *2 and no_end_indent and(abs(current_width-prev_width)<max_x_distance)
        )

        merged_this_round = False

        # 依次判断合并逻辑
        if overlap_x and overlap_y:
            # 水平合并
            prev_line["text"] = prev_line["text"].rstrip() + " " + line["text"].lstrip()

            if prev_indent :
                indent_val = prev_indent
                # print('当前合并2发的行','上一行：', prev_line["text"],'当前行:',line["text"] )
            else:
                if (px0 > x0):
                    indent_val = px0 - x0
                else:
                    indent_val = 0

            end_indent_val = abs(px1 - x1) if (px1 > x1 and abs(px1 - x1) > max_horizontal_gap) else 0
            merged[-1]["end_indent"] = end_indent_val

            merged[-1]["end_indent"] = end_indent_val
            new_x0 = min(px0, x0)
            new_y0 = min(py0, y0)
            new_x1 = max(px1, x1)
            new_y1 = max(py1, y1)
            prev_line["line_bbox"] = (new_x0, new_y0, new_x1, new_y1)
            prev_line["total_bold_chars"] += line["total_bold_chars"]
            prev_line["total_nonbold_chars"] += line["total_nonbold_chars"]
            prev_line["font_bold"] = prev_line["total_bold_chars"] > prev_line["total_nonbold_chars"]
            prev_line["font_names"].extend(line["font_names"])
            prev_line["font_names"] = list(set(prev_line["font_names"]))
            merged[-1]["indent"] = indent_val

            # print("重叠合并文本：", prev_line["text"])
            merged_this_round = True
        elif condition_1:

            merged[-1]["text"] = prev_line["text"].rstrip() + " " + line["text"].lstrip()

            new_x0 = min(px0, x0)
            new_y0 = min(py0, y0)
            new_x1 = max(px1, x1)
            new_y1 = max(py1, y1)
            merged[-1]["line_bbox"] = (new_x0, new_y0, new_x1, new_y1)
            merged[-1]["total_bold_chars"] += line["total_bold_chars"]
            merged[-1]["total_nonbold_chars"] += line["total_nonbold_chars"]
            merged[-1]["font_bold"] = merged[-1]["total_bold_chars"] > merged[-1]["total_nonbold_chars"]
            merged[-1]["font_names"].extend(line["font_names"])
            merged[-1]["font_names"] = list(set(merged[-1]["font_names"]))
            if line["font_size"] is not None and line["font_size"] > margin_in_middle * 2:
                merged[-1]["type"] = "title"
            # print('合并1', merged[-1]["text"])
            merged_this_round = True
        elif condition_2:
            # 如果上一行已经有缩进，直接继承
            if prev_indent :
                indent_val = prev_indent
                # print('当前合并2发的行','上一行：', prev_line["text"],'当前行:',line["text"] )
            else:
                if (px0 >x0):
                    indent_val = px0 - x0
                else:
                    indent_val = 0
            merged[-1]["indent"] = indent_val
            end_indent_val = abs(px1 - x1) if (px1 > x1 and abs(px1 - x1) > max_horizontal_gap) else 0
            merged[-1]["end_indent"] = end_indent_val
            merged[-1]["text"] = prev_line["text"].rstrip() + " " + line["text"].lstrip()

            new_x0 = min(px0, x0)
            new_y0 = min(py0, y0)
            new_x1 = max(px1, x1)
            new_y1 = max(py1, y1)
            merged[-1]["line_bbox"] = (new_x0, new_y0, new_x1, new_y1)
            merged[-1]["total_bold_chars"] += line["total_bold_chars"]
            merged[-1]["total_nonbold_chars"] += line["total_nonbold_chars"]
            merged[-1]["font_bold"] = merged[-1]["total_bold_chars"] > merged[-1]["total_nonbold_chars"]
            merged[-1]["font_names"].extend(line["font_names"])
            merged[-1]["font_names"] = list(set(merged[-1]["font_names"]))
            # print('合并2', indent_val ,end_indent_val,px0,x0,prev_line['indent'],merged[-1]["text"])
            # print("------")

            merged_this_round = True
        elif condition_5:

            # 如果上一行已经有缩进，直接继承
            if prev_line['indent']:
                indent_val = prev_line['indent']
            else:
                if (px0 > x0) :
                    indent_val = px0 - x0
                else:
                    indent_val = 0

            # 只在明显缩进时生效，否则为0

            merged[-1]["indent"] = indent_val

            end_indent_val = abs(px1 - x1) if (px1 > x1 and abs(px1 - x1) > max_horizontal_gap) else 0
            merged[-1]["end_indent"] = end_indent_val
            merged[-1]["text"] = prev_line["text"].rstrip() + " " + line["text"].lstrip()

            new_x0 = min(px0, x0)
            new_y0 = min(py0, y0)
            new_x1 = max(px1, x1)
            new_y1 = max(py1, y1)
            merged[-1]["line_bbox"] = (new_x0, new_y0, new_x1, new_y1)
            merged[-1]["total_bold_chars"] += line["total_bold_chars"]
            merged[-1]["total_nonbold_chars"] += line["total_nonbold_chars"]
            merged[-1]["font_bold"] = merged[-1]["total_bold_chars"] > merged[-1]["total_nonbold_chars"]
            merged[-1]["font_names"].extend(line["font_names"])
            merged[-1]["font_names"] = list(set(merged[-1]["font_names"]))
            # print('合并5', merged[-1]["text"], indent_val ,end_indent_val)
            merged_this_round = True

        elif condition_3:
            if (x1 - px1) > max_x_distance:
                merged.append(line)
                i += 1
                continue
            width_diff = abs(current_width - prev_width)
            if width_diff <= margin_in_middle / 2.0:
                merged_text = prev_line["text"].rstrip() + " " + line["text"].lstrip()
                indent_val = (x0 - px0) if (x0 > px0 and (x0 - px0) > (max_horizontal_gap / 2)) else 0
                merged[-1]["indent"] = indent_val
                end_indent_val = abs(px1 - x1) if (px1 > x1 and abs(px1 - x1) > max_horizontal_gap) else 0
                merged[-1]["end_indent"] = end_indent_val
                prev_line["text"] = merged_text


                new_x0 = min(px0, x0)
                new_y0 = min(py0, y0)
                new_x1 = max(px1, x1)
                new_y1 = max(py1, y1)
                prev_line["line_bbox"] = (new_x0, new_y0, new_x1, new_y1)
                prev_line["total_bold_chars"] += line["total_bold_chars"]
                prev_line["total_nonbold_chars"] += line["total_nonbold_chars"]
                prev_line["font_bold"] = prev_line["total_bold_chars"] > prev_line["total_nonbold_chars"]
                prev_line["font_names"].extend(line["font_names"])
                prev_line["font_names"] = list(set(prev_line["font_names"]))
                # print('合并3', merged[-1]["text"])
                merged_this_round = True
            else:
                if (prev_width < current_width) and (px0 > x0):
                    indent_val = (x0 - px0) if (x0 > px0 and (x0 - px0) > (max_horizontal_gap / 2)) else 0
                    merged[-1]["indent"] = indent_val
                    end_indent_val = abs(px1 - x1) if (px1 > x1 and abs(px1 - x1) > max_horizontal_gap) else 0
                    merged[-1]["end_indent"] = end_indent_val
                    merged_text = prev_line["text"].rstrip() + " " + line["text"].lstrip()
                    prev_line["text"] = merged_text


                    new_x0 = min(px0, x0)
                    new_y0 = min(py0, y0)
                    new_x1 = max(px1, x1)
                    new_y1 = max(py1, y1)
                    prev_line["line_bbox"] = (new_x0, new_y0, new_x1, new_y1)
                    prev_line["total_bold_chars"] += line["total_bold_chars"]
                    prev_line["total_nonbold_chars"] += line["total_nonbold_chars"]
                    prev_line["font_bold"] = prev_line["total_bold_chars"] > prev_line["total_nonbold_chars"]
                    prev_line["font_names"].extend(line["font_names"])
                    prev_line["font_names"] = list(set(prev_line["font_names"]))
                    # print('合并4', merged[-1]["text"])
                    merged_this_round = True
                elif (current_width < prev_width) and (x0 >= px0 + 2):
                    merged.append(line)
                    i += 1
                    continue
                else:
                    if prev_width < current_width:
                        indent_val = (x0 - px0) if (x0 > px0 and (x0 - px0) > (max_horizontal_gap / 2)) else 0
                        merged[-1]["indent"] = indent_val
                        end_indent_val = abs(px1 - x1) if (px1 > x1 and abs(px1 - x1) > max_horizontal_gap) else 0
                        merged[-1]["end_indent"] = end_indent_val
                        merged_text = prev_line["text"].rstrip() + " " + line["text"].lstrip()
                        prev_line["text"] = merged_text


                        new_x0 = min(px0, x0)
                        new_y0 = min(py0, y0)
                        new_x1 = max(px1, x1)
                        new_y1 = max(py1, y1)
                        prev_line["line_bbox"] = (new_x0, new_y0, new_x1, new_y1)
                        prev_line["total_bold_chars"] += line["total_bold_chars"]
                        prev_line["total_nonbold_chars"] += line["total_nonbold_chars"]
                        prev_line["font_bold"] = prev_line["total_bold_chars"] > prev_line["total_nonbold_chars"]
                        prev_line["font_names"].extend(line["font_names"])
                        prev_line["font_names"] = list(set(prev_line["font_names"]))
                        merged_this_round = True


        elif condition_4:
            merged[-1]["text"] = prev_line["text"].rstrip() + " " + line["text"].lstrip()

            new_x0 = min(px0, x0)
            new_y0 = min(py0, y0)
            new_x1 = max(px1, x1)
            new_y1 = max(py1, y1)
            indent_val = (x0 - px0) if (x0 > px0 and (x0 - px0) > (max_horizontal_gap / 2) )else 0
            merged[-1]["indent"] = indent_val
            end_indent_val = abs(px1 - x1) if (px1 > x1 and abs(px1 - x1) > max_horizontal_gap) else 0
            merged[-1]["end_indent"] = end_indent_val
            merged[-1]["line_bbox"] = (new_x0, new_y0, new_x1, new_y1)
            merged[-1]["total_bold_chars"] += line["total_bold_chars"]
            merged[-1]["total_nonbold_chars"] += line["total_nonbold_chars"]
            merged[-1]["font_bold"] = merged[-1]["total_bold_chars"] > merged[-1]["total_nonbold_chars"]
            merged[-1]["font_names"].extend(line["font_names"])
            merged[-1]["font_names"] = list(set(merged[-1]["font_names"]))
            # print('合并后的indent', merged[-1]["indent"])
            merged_this_round = True



        if merged_this_round:
            # 合并成功，i不递增，下一轮继续用当前prev_line和下一行比较
            i += 1
            continue
        else:
            # 没合并，推进下一个
            merged.append(line)
            i += 1

    return merged


def is_math(font_info_list, text_len, text, font_size):
    """
    判断文本是否为数学公式(或长度太短)。
    如果是数学公式，则返回 True。
    如果长度很短且几乎全为数字/标点/符号，则返回 "abandon"。
    否则返回 False。
    """

    # 用于去除空格计算长度
    text_length_nospaces = len(text.replace(" ", ""))

    # 若行整体文本长度很短，且字体集合与“数学字体”有交集，则直接视为 math.暂时改为1.0
    if text_length_nospaces < font_size * 1.0:
        font_set = set(font_info_list)
        if font_set & MATH_FONTS_SET:
            # print('math,', text)
            return True

    # 如果文字过短，就检查每个字符是否都是数字/标点/符号/空白
    if text_len < 1.5 * font_size:
        all_special_chars = True
        stripped_text = text.strip()
        for ch in stripped_text:
            cat = unicodedata.category(ch)
            # 允许通过的情况：
            # 1. 数字 (cat == 'Nd')
            # 2. 标点 (cat.startswith('P'))
            # 3. 符号 (cat.startswith('S'))，包括 Sm (数学符号)、So (其他符号)
            # 4. 空格或其他空白符 (cat.startswith('Z'))
            #    - 或者你可以直接用 ch.isspace() 来判断空格
            if not (
                    cat == 'Nd'
                    or cat.startswith('P')
                    or cat.startswith('S')
                    or cat.startswith('Z')
            ):
                # 如果发现不属于上述几类，则判定为非“纯数字/标点/符号”
                all_special_chars = False
                break

        # 如果所有字符都在我们的“允许”范围内，则标记为 "abandon"
        if all_special_chars:
            # print(stripped_text, '纯数字/标点/符号，标记为abandon')
            return "abandon"

        return False

    # 其它情况默认不视为 math
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


def get_new_blocks(page, pdf_path=None, page_num=None):
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

        if pdf_path and page_num:
            pdf_document = fitz.open(pdf_path)
            if page_number < 1 or page_number > pdf_document.page_count:
                print(f"页码 {page_number} 超出范围（1 - {pdf_document.page_count}）")
                return

            page = pdf_document[page_number - 1]

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

                filtered_spans = [span for span in spans if span.get("text", "").strip() != ""]
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
                    "font_name": chosen_font_name,  # 仅代表字体名称
                    "font_names": list(font_names_set),  # 全部子span字体集合
                    "rotation_angle": angle,
                    "type": "plain_text",  # 初始行类型
                    "font_bold": line_is_bold,
                    "indent": 0,
                    "end_indent": 0,
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
            check_font_size=False,
            check_font_name=False,
            check_font_color=False
        )

        # ============= (2) 垂直合并 =============
        merged_final = merge_lines(
            merged_horizontally,
            check_font_size=False,
            check_font_name=False,
            check_font_color=False,
            check_same_block=False
        )

        # ============= (3) 基于合并后行信息，构建临时数据结构 =============
        #    存储块号 -> [ (行在 merged_final 列表中的索引, 字符长度, 行类型) ... ]，
        #    并统计块内总字符数。
        temp_block_dict = defaultdict(lambda: {
            'lines': [],  # [(merged_final_idx, line_type, text_len), ...]
            'total_chars': 0  # 整个 block 的字符串长度总和
        })

        for idx, line_info in enumerate(merged_final):
            # 计算该行字符长度
            text_len = line_info['total_bold_chars'] + line_info['total_nonbold_chars']
            # 判断是否是 math（行类型先设置，这里只是初步）
            final_text = line_info['text'] or ''

            if final_text:
                result = is_math(line_info['font_names'], text_len, final_text, line_info['font_size'])
                if result == True:
                    line_info['type'] = 'math'
                elif result == "abandon":
                    line_info['type'] = 'abandon'
            else:
                line_info['type'] = 'abandon'

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

        # ============= (6) 打印结果并构造返回值 ============= 115行
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
            # print(f" 末尾缩进(indent): {line_info['end_indent']}")
            # print(f" total_bold_chars = {line_info['total_bold_chars']}, total_nonbold_chars = {line_info['total_nonbold_chars']}")
            # print(f" 行类型(type): {line_info['type']}")
            # print("-" * 50)

            # 排除被标记为 abandon 的块
            if line_info['type'] != 'abandon':
                new_blocks.append([
                    line_info['text'],
                    tuple(line_info['line_bbox']),
                    line_info['type'],
                    line_info['rotation_angle'],
                    line_info['font_color'],
                    line_info['indent'],
                    line_info['font_bold'],
                    line_info['font_size'],
                    line_info['end_indent']
                ])

        return new_blocks

    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    b = datetime.datetime.now()
    pdf_path = "m2.pdf"  # 换成你的 PDF 文件路径
    page_number = 4 # 换成想处理的页码
    z = get_new_blocks(page=None, pdf_path=pdf_path, page_num=page_number)
    print("最终返回的 new_blocks:", z)
    e = datetime.datetime.now()
    elapsed_time = (e - b).total_seconds()
    print(f"运行时间: {elapsed_time} 秒")
