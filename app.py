import streamlit as st
import subprocess
import sys
import pandas as pd
from datetime import date
from pathlib import Path

st.set_page_config(page_title="海事舆情每日监测平台", layout="centered")

st.title("📅 海事舆情每日监测平台")

selected_date = st.date_input("请选择查询日期：", value=date.today())
selected_date_str = selected_date.strftime('%Y-%m-%d')

if st.button("🔍 查询"):
    with st.spinner("正在运行爬虫，请稍候..."):
        # 拼接命令
        command = [sys.executable, "run.py", "--date", selected_date_str]
        
        # 执行 run.py 并捕获输出
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', check=True)
            output_text = result.stdout
            st.success("✅ 查询成功，正在解析结果...")
        except subprocess.CalledProcessError as e:
            st.error("❌ 爬虫运行失败！")
            st.text(e.stderr)
            st.stop()

        # 显示终端输出（可选）
        with st.expander("📄 运行日志"):
            st.text(output_text)

        # 读取 CSV 并显示
        csv_path = Path(f"results_{selected_date_str}.csv")
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            st.success(f"✅ 查询成功，共 {len(df)} 条记录：")
            st.dataframe(df, use_container_width=True)

            # 提供下载
            st.download_button(
                label="📥 下载 CSV",
                data=csv_path.read_bytes(),
                file_name=csv_path.name,
                mime="text/csv"
            )
        else:
            st.warning("⚠ 没有找到结果文件，请检查 run.py 是否执行成功。")
