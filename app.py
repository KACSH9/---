# app.py - 最简工作版
import streamlit as st
import subprocess
import sys
import pandas as pd
import datetime
from pathlib import Path

# 页面配置
st.set_page_config(
    page_title="海事舆情每日监测平台",
    page_icon="📅",
    layout="wide"
)

st.title("📅 海事舆情每日监测平台")
st.markdown("---")

def parse_run_output_line(line):
    """解析run.py的输出行"""
    line = line.strip()

    # 处理错误信息
    if "[Error]" in line and "调用" in line:
        try:
            if "失败" in line:
                script_part = line.split("调用")[1].split("失败")[0].strip()
                return (script_part, "", "", "error")
            elif "超时" in line:
                script_part = line.split("调用")[1].split("超时")[0].strip()
                return (script_part, "", "", "timeout")
        except:
            return ("未知脚本", "", "", "error")

    if "▶" not in line:
        return None

    # 分割脚本名和内容
    parts = line.split("▶", 1)
    if len(parts) != 2:
        return None

    script = parts[0].strip()
    content = parts[1].strip()

    # 检查是否是"没有找到"的消息
    if "✖" in content or "没有找到" in content:
        return (script, "", "", "no_match")

    # 解析标题和链接
    content_parts = content.split()
    if not content_parts:
        return (script, "", "", "empty")

    # 从后往前找第一个以http开头的部分作为链接
    link = ""
    title_parts = content_parts

    for i in range(len(content_parts) - 1, -1, -1):
        part = content_parts[i]
        if part.startswith("http"):
            link = part
            title_parts = content_parts[:i]
            break

    title = " ".join(title_parts).strip()

    if title or link:
        status = "success"
    else:
        status = "empty"

    return (script, title, link, status)

# 主界面
col1, col2 = st.columns([3, 1])

with col1:
    date_input = st.date_input(
        "请选择查询日期:",
        value=datetime.date.today()
    )

with col2:
    st.write("")
    st.write("")
    query_button = st.button("🔍 开始查询", type="primary", use_container_width=True)

# 查询逻辑
if query_button:
    date_str = date_input.strftime("%Y-%m-%d")
    
    # 检查run.py是否存在
    if not Path("run.py").exists():
        st.error("❌ 找不到 run.py 文件")
        st.stop()

    # 构建命令
    command = [sys.executable, "run.py", "--date", date_str]
    
    # 显示查询状态
    with st.spinner("🔄 正在查询，请稍候..."):
        try:
            # 执行命令
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                timeout=300,  # 5分钟超时
                cwd="."
            )
            
            st.write(f"**执行命令:** `{' '.join(command)}`")
            st.write(f"**返回码:** {result.returncode}")
            
            # 处理结果
            if result.returncode != 0:
                st.error("❌ 查询失败")
                if result.stderr:
                    st.code(result.stderr)
                if result.stdout:
                    st.text("标准输出:")
                    st.code(result.stdout)
            else:
                st.success("✅ 查询完成")
                
                # 显示原始输出（调试用）
                if result.stdout:
                    with st.expander("🔍 原始输出", expanded=True):
                        st.code(result.stdout)
                
                # 解析输出
                data = []
                output_lines = result.stdout.splitlines()
                
                st.write(f"**输出行数:** {len(output_lines)}")
                
                for i, line in enumerate(output_lines):
                    if not line.strip():
                        continue
                        
                    # 跳过不相关的行
                    if line.startswith("✅") or "已将结果导出到" in line:
                        continue
                        
                    parsed = parse_run_output_line(line)
                    if parsed:
                        script, title, link, status = parsed
                        data.append({
                            'script': script,
                            'title': title,
                            'link': link,
                            'status': status
                        })
                        st.write(f"✅ 解析成功: {script} -> {status}")
                    else:
                        st.write(f"⚠️ 无法解析: {line}")

                st.write(f"**解析到的数据条数:** {len(data)}")

                if data:
                    df = pd.DataFrame(data)

                    # 统计
                    total = len(df)
                    success = len(df[df['status'] == 'success'])
                    no_match = len(df[df['status'] == 'no_match'])
                    error = len(df[df['status'].isin(['error', 'timeout'])])

                    # 显示统计
                    st.markdown("### 📊 查询结果统计")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("总数据源", total)
                    with col2:
                        st.metric("✅ 成功", success)
                    with col3:
                        st.metric("⚠️ 无匹配", no_match)
                    with col4:
                        st.metric("❌ 错误", error)

                    # 筛选选项
                    show_filter = st.selectbox(
                        "显示筛选:",
                        ["全部", "仅成功", "仅错误", "仅无匹配"],
                        index=0
                    )

                    # 应用筛选
                    if show_filter == "仅成功":
                        filtered_df = df[df['status'] == 'success']
                    elif show_filter == "仅错误":
                        filtered_df = df[df['status'].isin(['error', 'timeout'])]
                    elif show_filter == "仅无匹配":
                        filtered_df = df[df['status'] == 'no_match']
                    else:
                        filtered_df = df.copy()

                    # 显示数据
                    if len(filtered_df) > 0:
                        # 准备显示数据
                        display_df = filtered_df.copy()

                        # 状态符号化
                        status_map = {
                            'success': '✅',
                            'no_match': '⚠️',
                            'empty': '📝',
                            'error': '❌',
                            'timeout': '⏰'
                        }
                        display_df['状态'] = display_df['status'].map(status_map)

                        # 选择显示列
                        display_df = display_df[['script', 'title', 'link', '状态']].rename(columns={
                            'script': '数据源',
                            'title': '标题',
                            'link': '链接'
                        })

                        st.dataframe(
                            display_df,
                            use_container_width=True,
                            hide_index=True
                        )

                        # 下载按钮
                        csv_data = filtered_df[['script', 'title', 'link']].to_csv(index=False, encoding='utf-8')
                        st.download_button(
                            label="📥 下载 CSV",
                            data=csv_data.encode('utf-8'),
                            file_name=f"海事舆情_{date_str}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("ℹ️ 当前筛选条件下无结果")
                else:
                    st.warning("⚠️ 没有解析到任何数据")

        except subprocess.TimeoutExpired:
            st.error("❌ 查询超时（5分钟）")
        except Exception as e:
            st.error(f"❌ 发生错误: {str(e)}")
            st.code(str(e))
