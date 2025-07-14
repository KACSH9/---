# app.py
import streamlit as st
import sys
import subprocess
import pandas as pd
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).parent
RUN_SCRIPT = BASE_DIR / "run.py"

st.set_page_config(page_title="舆情信息查询平台", layout="centered")
st.title("📅 海事舆情每日监测平台")

# 日期输入
date = st.date_input("请选择查询日期：")
date_str = date.strftime("%Y-%m-%d")

if st.button("🔍 查询"):
    # 调试目录
    st.write("当前目录文件：", [p.name for p in BASE_DIR.iterdir()])

    # 调用 run.py 生成 CSV
    try:
        result = subprocess.run(
            [sys.executable, str(RUN_SCRIPT), "-d", date_str],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            check=True
        )
        st.text(result.stdout)  # 可选：把 run.py 的输出也展示在页面上
    except subprocess.CalledProcessError as e:
        st.error(f"运行爬虫时出错（脚本异常）：\n{e.stderr}")
        st.stop()
    except Exception as e:
        st.error(f"运行爬虫时出错：{e}")
        st.stop()

    # 读取结果 CSV
    csv_path = BASE_DIR / f"results_{date_str}.csv"
    if not csv_path.exists():
        st.warning("未找到结果文件，可能没有该日期的数据。")
        st.stop()

    df = pd.read_csv(csv_path, encoding="utf-8")
    if df.empty:
        st.warning("未获取到任何数据。")
    else:
        st.success(f"查询成功，共 {len(df)} 条记录：")
        st.dataframe(df)
        st.download_button(
            "📥 下载 CSV",
            df.to_csv(index=False, encoding="utf-8"),
            file_name=csv_path.name,
            mime="text/csv"
        )
