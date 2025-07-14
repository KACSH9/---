#!/usr/bin/env python3
# run.py

import argparse
import subprocess
import sys
import csv
from pathlib import Path

def run_and_get_matches(script_path, date_str):
    """
    运行脚本并返回所有包含 date_str 的原始输出行列表。
    如果脚本运行失败，返回 None。
    """
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"[Error] 调用 {script_path} 失败：", e.stderr, file=sys.stderr)
        return None

    matches = []
    for line in result.stdout.splitlines():
        if date_str in line:
            matches.append(line.strip())
    return matches

def parse_line_to_fields(line, date_str):
    """
    给定一行形如 "YYYY-MM-DD  Title  URL"，拆成 (title, link)。
    """
    # 把日期部分去掉
    rest = line.replace(date_str, "").strip()
    if not rest:
        return ("", "")
    parts = rest.split()
    link = parts[-1]
    title = " ".join(parts[:-1])
    return (title, link)

def main():
    parser = argparse.ArgumentParser(description="运行爬虫并筛选指定日期的结果，CSV 输出三列：脚本, 标题, 链接")
    parser.add_argument(
        "--date", "-d",
        required=True,
        help="要筛选的日期，格式为 YYYY-MM-DD"
    )
    parser.add_argument(
        "--out", "-o",
        default=None,
        help="可选：指定输出 CSV 文件路径；默认 results_<date>.csv"
    )
    args = parser.parse_args()

    date_str = args.date
    scripts = [
        "中国外交部.py", "国际海事组织.py", "世界贸易组织.py", "日本外务省.py", "联合国海洋法庭.py", "国际海底管理局.py",
        "战略与国际研究中心.py", "美国国务院.py", "美国运输部海事管理局.py", "中国海事局.py", "日本海上保安大学校.py",
        "日本海上保安厅.py", "太平洋岛国论坛.py", "越南外交部.py", "越南外交学院.py", "中国国际电视台官微.py", "南海之声.py"
    ]

    # 收集最终行：each is (script, title, link)
    all_rows = []

    for script in scripts:
        matches = run_and_get_matches(script, date_str)
        if matches is None:
            continue  # 跳过出错的脚本

        if matches:
            for raw in matches:
                title, link = parse_line_to_fields(raw, date_str)
                print(f"{script} ▶ {title}  {link}")
                all_rows.append((script, title, link))
        else:
            # 无匹配时也写入一行，空标题和链接
            print(f"{script} ▶ ✖ 没有找到包含 '{date_str}' 的记录")
            all_rows.append((script, "", ""))

    # 写入 CSV
    out_path = args.out or f"results_{date_str}.csv"
    out_file = Path(out_path)
    try:
        with out_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["script", "title", "link"])
            for row in all_rows:
                writer.writerow(row)
        print(f"\n✅ 已将结果导出到：{out_file.resolve()}")
    except Exception as e:
        print(f"[Error] 写入 CSV 文件失败：{e}", file=sys.stderr)

if __name__ == "__main__":
    main()


