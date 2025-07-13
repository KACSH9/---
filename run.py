#!/usr/bin/env python3
# run.py

import argparse
import subprocess
import sys
import csv
from pathlib import Path

def run_and_get_matches(script_path, date_str):
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"{script_path} ▶ 执行失败：{e.stderr.strip()}")
        return [f"{script_path} ▶ ✖ 执行失败：{e.stderr.strip()}"]

    matches = []
    for line in result.stdout.splitlines():
        if date_str in line:
            matches.append(line.strip())
    return matches if matches else [f"{script_path} ▶ ✖ 没有找到包含 '{date_str}' 的记录"]

def parse_line_to_fields(line, date_str):
    if "✖" in line or "执行失败" in line:
        parts = line.split("▶", 1)
        return parts[0].strip(), parts[1].strip(), ""
    rest = line.replace(date_str, "").strip()
    if not rest:
        return ("", "", "")
    parts = rest.rsplit(" ", 1)
    if len(parts) < 2:
        return ("", rest, "")
    return ("", parts[0], parts[1])

def main():
    parser = argparse.ArgumentParser(description="运行爬虫并筛选指定日期的结果，CSV 输出三列：脚本, 标题, 链接")
    parser.add_argument("--date", "-d", required=True, help="要筛选的日期，格式为 YYYY-MM-DD")
    parser.add_argument("--out", "-o", default=None, help="指定输出 CSV 文件路径；默认 results_<date>.csv")
    args = parser.parse_args()

    date_str = args.date
    scripts = [
        "中国外交部.py", "国际海事组织.py", "世界贸易组织.py", "日本外务省.py", "联合国海洋法庭.py", "国际海底管理局.py",
        "战略与国际研究中心.py", "美国国务院.py", "美国运输部海事管理局.py", "中国海事局.py", "日本海上保安大学校.py",
        "日本海上保安厅.py", "太平洋岛国论坛.py", "越南外交部.py", "越南外交学院.py"
    ]

    all_rows = []

    for script in scripts:
        matches = run_and_get_matches(script, date_str)
        for raw in matches:
            script_name, title, link = parse_line_to_fields(raw, date_str)
            all_rows.append((script_name or script, title, link))
            print(f"{script_name or script} ▶ {title} {link}")

    out_path = args.out or f"results_{date_str}.csv"
    out_file = Path(out_path)
    try:
        with out_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["script", "title", "link"])
            writer.writerows(all_rows)
        print(f"\n✅ 已将结果导出到：{out_file.resolve()}")
    except Exception as e:
        print(f"[Error] 写入 CSV 文件失败：{e}", file=sys.stderr)

if __name__ == "__main__":
    main()
