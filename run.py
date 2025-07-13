#!/usr/bin/env python3
# run.py
import argparse
import subprocess
import sys
import csv
from pathlib import Path
import os

def run_and_get_matches(script_path, date_str):
    """
    运行脚本并返回所有包含 date_str 的原始输出行列表。
    如果脚本运行失败，返回 None。
    """
    # 获取脚本的完整路径
    script_full_path = Path(script_path).resolve()
    
    # 检查脚本是否存在
    if not script_full_path.exists():
        print(f"[Warning] 脚本不存在：{script_full_path}", file=sys.stderr)
        return None
    
    try:
        # 确保在脚本所在目录运行
        script_dir = script_full_path.parent
        result = subprocess.run(
            [sys.executable, str(script_full_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            check=True,
            cwd=str(script_dir)  # 设置工作目录
        )
    except subprocess.CalledProcessError as e:
        print(f"[Error] 调用 {script_path} 失败：", e.stderr, file=sys.stderr)
        return None
    except Exception as e:
        print(f"[Error] 运行 {script_path} 时发生未知错误：{e}", file=sys.stderr)
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
    if len(parts) >= 2:
        link = parts[-1]
        title = " ".join(parts[:-1])
    else:
        title = rest
        link = ""
    
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
        help="可选：指定输出 CSV 文件路径；默认 results_.csv"
    )
    args = parser.parse_args()
    date_str = args.date
    
    # 获取当前脚本的目录
    current_dir = Path(__file__).parent.resolve()
    
    scripts = [
        "中国外交部.py", "国际海事组织.py", "世界贸易组织.py", "日本外务省.py", "联合国海洋法庭.py", "国际海底管理局.py",
        "战略与国际研究中心.py", "美国国务院.py", "美国运输部海事管理局.py", "中国海事局.py", "日本海上保安大学校.py",
        "日本海上保安厅.py", "太平洋岛国论坛.py", "越南外交部.py", "越南外交学院.py"
    ]
    
    # 打印调试信息
    print(f"[Debug] 当前目录：{current_dir}")
    print(f"[Debug] 开始处理 {len(scripts)} 个脚本...")
    
    # 收集最终行：each is (script, title, link)
    all_rows = []
    processed_count = 0
    
    for script in scripts:
        # 构建脚本的完整路径
        script_path = current_dir / script
        
        print(f"[Debug] 处理脚本：{script_path}")
        
        matches = run_and_get_matches(str(script_path), date_str)
        
        if matches is None:
            # 脚本运行失败
            print(f"{script} ▶ ❌ 脚本运行失败")
            all_rows.append((script, "脚本运行失败", ""))
        elif matches:
            # 有匹配结果
            for raw in matches:
                title, link = parse_line_to_fields(raw, date_str)
                print(f"{script} ▶ {title}  {link}")
                all_rows.append((script, title, link))
            processed_count += 1
        else:
            # 无匹配结果
            print(f"{script} ▶ ✖ 没有找到包含 '{date_str}' 的记录")
            all_rows.append((script, f"没有找到包含 {date_str} 的记录", ""))
            processed_count += 1
    
    print(f"[Debug] 成功处理 {processed_count}/{len(scripts)} 个脚本")
    
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
    print(f"[Debug] 成功处理 {processed_count}/{len(scripts)} 个脚本")
    
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
