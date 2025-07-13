import streamlit as st
import subprocess
import sys
import csv
from pathlib import Path
import datetime

st.set_page_config(page_title="海事舆情每日监测平台", page_icon="📅")

st.title("📅 海事舆情每日监测平台")
date_input = st.text_input("请选择查询日期：", value=str(datetime.date.today()))

if st.button("🔍 查询"):
    with st.spinner("查询中，请稍候..."):
        scripts = [
            "中国外交部.py", "国际海事组织.py", "世界贸易组织.py", "日本外务省.py", "联合国海洋法庭.py", "国际海底管理局.py",
            "战略与国际研究中心.py", "美国国务院.py", "美国运输部海事管理局.py", "中国海事局.py", "日本海上保安大学校.py",
            "日本海上保安厅.py", "太平洋岛国论坛.py", "越南外交部.py", "越南外交学院.py"
        ]

        date_str = date_input.strip()
        results = []
        logs = []

        for script in scripts:
            try:
                result = subprocess.run(
                    [sys.executable, script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding='utf-8',
                    check=True
                )
                matched_lines = [
                    line.strip() for line in result.stdout.splitlines()
                    if "▶" in line
                ]
                if matched_lines:
                    for line in matched_lines:
                        script_name, rest = line.split("▶", 1)
                        parts = rest.strip().rsplit(" ", 1)
                        if len(parts) == 2:
                            title, link = parts
                            results.append((script_name.strip(), title.strip(), link.strip()))
                        else:
                            results.append((script_name.strip(), rest.strip(), ""))
                else:
                    logs.append(f"{script} 没有匹配记录")
                    results.append((script, "", ""))
            except subprocess.CalledProcessError as e:
                logs.append(f"[ERROR] {script} 执行失败：{e.stderr.strip()}")
                results.append((script, "", ""))

        # 仅显示非空标题的记录
        display_results = [r for r in results if r[1]]
        st.success(f"✅ 查询成功，共 {len(display_results)} 条记录：")
        st.dataframe(display_results, use_container_width=True)

        # 下载 CSV
        csv_path = f"results_{date_str}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["script", "title", "link"])
            writer.writerows(display_results)

        with open(csv_path, "rb") as f:
            st.download_button("📥 下载 CSV", f, file_name=csv_path)

        # 展示运行日志
        with st.expander("📄 运行日志"):
            for log in logs:
                st.write(log)

