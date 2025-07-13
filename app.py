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
        command = [sys.executable, "run.py", "--date", date_input.strip()]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')

        if result.returncode != 0:
            st.error(f"运行失败：{result.stderr.strip()}")
        else:
            output_lines = [line for line in result.stdout.splitlines() if "▶" in line]
            results = []
            for line in output_lines:
                script, rest = line.split("▶", 1)
                script, rest = script.strip(), rest.strip()
                title, link = rest.rsplit(" ", 1) if "http" in rest else (rest, "")
                results.append((script, title, link))

            df = pd.DataFrame(results, columns=["script", "title", "link"])
            st.success(f"✅ 查询成功，共 {len(df[df['link']!=''])} 条有效记录：")
            st.dataframe(df, use_container_width=True)

            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 下载 CSV", csv_data, f"results_{date_input}.csv", "text/csv")

            with st.expander("📄 运行日志"):
                st.code(result.stdout)

