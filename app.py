# app.py

import streamlit as st
import subprocess
import sys
import pandas as pd
import datetime

# 页面配置
st.set_page_config(page_title="海事舆情每日监测平台", page_icon="📅")
st.title("📅 海事舆情每日监测平台")

# 日期输入
date_input = st.text_input("请选择查询日期：", value=str(datetime.date.today()))

# 查询按钮
if st.button("🔍 查询"):
    with st.spinner("查询中，请稍候..."):
        date_str = date_input.strip()

        # 调用 run.py，传入 --date 参数
        cmd = [sys.executable, "run.py", "--date", date_str]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")

        # 如果 run.py 返回非零，就展示错误
        if proc.returncode != 0:
            st.error(f"运行失败：\n```\n{proc.stderr.strip()}\n```")
        else:
            # 只保留包含“▶”的行
            lines = [L for L in proc.stdout.splitlines() if "▶" in L]

            # 解析成 (script, title, link)
            data = []
            for line in lines:
                # 格式：脚本名 ▶ 标题 链接
                script, rest = line.split("▶", 1)
                script = script.strip()
                rest   = rest.strip()
                # 最后一个空格前分割 title 和 link
                if " " in rest:
                    title, link = rest.rsplit(" ", 1)
                else:
                    title, link = rest, ""
                data.append((script, title.strip(), link.strip()))

            # DataFrame
            df = pd.DataFrame(data, columns=["script", "title", "link"])

            # 展示
            st.success(f"✅ 查询成功，共 {len(df[df['link']!=''])} 条有效记录：")
            st.dataframe(df, use_container_width=True)

            # 下载 CSV
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 下载 CSV",
                data=csv_bytes,
                file_name=f"results_{date_str}.csv",
                mime="text/csv"
            )

            # 展示原始日志
            with st.expander("📄 运行日志"):
                st.code(proc.stdout)
