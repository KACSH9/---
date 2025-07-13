import streamlit as st
import subprocess
import sys
import pandas as pd
import datetime

st.set_page_config(page_title="海事舆情每日监测平台", page_icon="📅")

st.title("📅 海事舆情每日监测平台")
date_input = st.text_input("请选择查询日期：", value=str(datetime.date.today()))

if st.button("🔍 查询"):
    with st.spinner("查询中，请稍候..."):
        date_str = date_input.strip()

        # 改用run.py，注意这里是关键
        command = [sys.executable, "run.py", "--date", date_str]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8'
        )

        if result.returncode != 0:
            st.error(f"运行失败：{result.stderr.strip()}")
        else:
            output = result.stdout
            matched_lines = [
                line for line in output.splitlines()
                if "▶" in line
            ]

            results = []
            for line in matched_lines:
                script, rest = line.split("▶", 1)
                script = script.strip()
                rest = rest.strip()
                parts = rest.rsplit(" ", 1)
                if len(parts) == 2:
                    title, link = parts
                    results.append((script, title.strip(), link.strip()))
                else:
                    results.append((script, rest.strip(), ""))

            df = pd.DataFrame(results, columns=["script", "title", "link"])

            # 显示结果数量
            st.success(f"✅ 查询成功，共 {len(df)} 条记录：")

            # 显示表格
            st.dataframe(df, use_container_width=True)

            # 提供下载csv
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 下载 CSV",
                data=csv_data,
                file_name=f"results_{date_str}.csv",
                mime="text/csv",
            )

            # 显示运行日志
            with st.expander("📄 运行日志"):
                st.code(result.stdout)
