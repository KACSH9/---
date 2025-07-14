import streamlit as st
import subprocess
import sys
import os

# Streamlit 页面设置
st.set_page_config(page_title="网站抓取系统", layout="wide")
st.title("📌 网站抓取系统")

# 获取当前目录下所有的.py脚本
scripts = [f for f in os.listdir('.') if f.endswith('.py') and f not in ['run.py', 'app.py']]

# 选择要运行的脚本
selected_script = st.selectbox('选择要抓取的网站脚本：', scripts)

# 输入日期
selected_date = st.date_input('选择日期：')
date_str = selected_date.strftime('%Y-%m-%d')

# 定义函数运行抓取脚本
def run_script(script_name, date_str):
    try:
        result = subprocess.run(
            [sys.executable, 'run.py', script_name, date_str],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            check=True
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        st.error(f"运行脚本出错: {e.stderr}")
        return []

# 添加按钮触发抓取
if st.button('🚀 开始抓取'):
    with st.spinner('正在抓取数据，请稍候...'):
        lines = run_script(selected_script, date_str)

        if not lines:
            st.warning("没有抓取到相关数据，请检查脚本或日期是否正确。");
        else:
            st.success(f"抓取完成，共 {len(lines)} 条记录。");
            for line in lines:
                parts = line.strip().split()
                # 假设脚本输出格式为：日期 题目 链接
                if len(parts) >= 3:
                    date = parts[0]
                    title = " ".join(parts[1:-1])
                    link = parts[-1]
                    st.markdown(f"- 📅 **{date}** [{title}]({link})")
                else:
                    st.write(line)

