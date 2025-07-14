#!/usr/bin/env python3
# run.py - 智能优化版

import argparse
import subprocess
import sys
import csv
from pathlib import Path
import time

def run_and_get_matches(script_path, date_str, timeout=30):
    """
    运行脚本并返回所有包含 date_str 的原始输出行列表。
    如果脚本运行失败，返回 None。
    """
    print(f"[INFO] 开始处理脚本: {script_path} (超时: {timeout}秒)")
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            check=True,
            timeout=timeout
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"[INFO] {script_path} 执行成功，耗时 {execution_time:.1f}秒")
        
    except subprocess.TimeoutExpired:
        print(f"[Error] 调用 {script_path} 超时（{timeout}秒）")
        return None
    except subprocess.CalledProcessError as e:
        print(f"[Error] 调用 {script_path} 失败：", e.stderr.strip() if e.stderr.strip() else "未知错误")
        return None
    except Exception as e:
        print(f"[Error] 调用 {script_path} 发生未知错误：{str(e)}")
        return None

    matches = []
    for line in result.stdout.splitlines():
        if date_str in line:
            matches.append(line.strip())
    
    print(f"[INFO] {script_path} 找到 {len(matches)} 条匹配记录")
    return matches

def parse_line_to_fields(line, date_str):
    """
    给定一行形如 "YYYY-MM-DD  Title  URL"，拆成 (title, link)。
    """
    rest = line.replace(date_str, "").strip()
    if not rest:
        return ("", "")
    parts = rest.split()
    if not parts:
        return ("", "")
    
    # 最后一个以http开头的是链接
    link = ""
    title_parts = parts
    
    for i in range(len(parts) - 1, -1, -1):
        if parts[i].startswith("http"):
            link = parts[i]
            title_parts = parts[:i]
            break
    
    title = " ".join(title_parts)
    return (title, link)

def main():
    parser = argparse.ArgumentParser(description="智能运行爬虫并筛选指定日期的结果")
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
    parser.add_argument(
        "--fast", 
        action="store_true",
        help="快速模式：跳过已知慢的脚本"
    )
    
    args = parser.parse_args()
    date_str = args.date
    
    # 脚本分类：根据经验和观察分为快、中、慢三类
    fast_scripts = [
        "中国外交部.py",
        "越南外交部.py", 
        "越南外交学院.py",
        "中国海事局.py"
    ]
    
    medium_scripts = [
        "国际海事组织.py",
        "世界贸易组织.py", 
        "联合国海洋法庭.py",
        "国际海底管理局.py",
        "战略与国际研究中心.py",
        "美国国务院.py",
        "美国运输部海事管理局.py",
        "太平洋岛国论坛.py"
    ]
    
    # 这些是经常出错或很慢的脚本
    slow_scripts = [
        "日本外务省.py",
        "日本海上保安大学校.py", 
        "日本海上保安厅.py"
    ]
    
    # 设置不同的超时时间
    timeouts = {
        'fast': 20,      # 快速脚本：20秒超时
        'medium': 40,    # 中等脚本：40秒超时  
        'slow': 15       # 慢脚本：15秒快速超时（经常出错，快速跳过）
    }
    
    if args.fast:
        print("[INFO] 快速模式：跳过已知慢的脚本")
        all_scripts = fast_scripts + medium_scripts
    else:
        print("[INFO] 完整模式：处理所有脚本")
        all_scripts = fast_scripts + medium_scripts + slow_scripts
    
    print(f"[INFO] 开始处理 {len(all_scripts)} 个脚本")
    
    all_rows = []
    processed_count = 0
    
    # 按类别处理脚本
    script_categories = [
        (fast_scripts, 'fast', '快速脚本'),
        (medium_scripts, 'medium', '中等脚本'), 
        (slow_scripts, 'slow', '慢速脚本（快速超时）')
    ]
    
    for scripts, category, desc in script_categories:
        if args.fast and category == 'slow':
            continue
            
        if not scripts:
            continue
            
        print(f"\n[INFO] === 开始处理 {desc} ({len(scripts)} 个) ===")
        timeout = timeouts[category]
        
        for script in scripts:
            processed_count += 1
            
            # 检查文件是否存在
            if not Path(script).exists():
                print(f"[WARNING] {script} 文件不存在，跳过")
                all_rows.append((script, "", ""))
                continue
            
            print(f"[INFO] 进度 {processed_count}/{len(all_scripts)}: {script}")
            
            matches = run_and_get_matches(script, date_str, timeout)
            
            if matches is None:
                # 脚本执行失败，快速跳过
                all_rows.append((script, "", ""))
                continue

            if matches:
                for raw in matches:
                    title, link = parse_line_to_fields(raw, date_str)
                    print(f"{script} ▶ {title}  {link}")
                    all_rows.append((script, title, link))
            else:
                print(f"{script} ▶ ✖ 没有找到包含 '{date_str}' 的记录")
                all_rows.append((script, "", ""))

    print(f"\n[INFO] 所有脚本处理完成")
    
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
        print(f"[Error] 写入 CSV 文件失败：{e}")

if __name__ == "__main__":
    main()
