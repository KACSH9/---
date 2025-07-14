# app.py - 简化可用版
import streamlit as st
import subprocess
import sys
import pandas as pd
import datetime
from pathlib import Path
import time

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
    
    # 找链接
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

# 环境检查
run_py_exists = Path("run.py").exists()

if not run_py_exists:
    st.error("❌ 找不到 run.py 文件")
    st.stop()

# 主界面
col1, col2 = st.columns([2, 1])

with col1:
    date_input = st.date_input(
        "选择查询日期:",
        value=datetime.date.today()
    )

with col2:
    run_mode = st.selectbox(
        "运行模式:",
        ["🚀 快速模式", "🔧 完整模式"],
        index=0
    )
    fast_mode = "快速" in run_mode

st.markdown("---")

query_button = st.button("🔍 开始查询", type="primary", use_container_width=True)

# 查询逻辑
if query_button:
    date_str = date_input.strftime("%Y-%m-%d")
    
    # 显示状态
    status_placeholder = st.empty()
    progress_placeholder = st.empty()
    
    with st.container():
        st.info(f"🔄 开始查询 {date_str}，模式：{run_mode}")
        
        # 构建命令
        command = [sys.executable, "run.py", "--date", date_str]
        if fast_mode:
            command.append("--fast")
        
        st.text(f"执行命令: {' '.join(command)}")
        
        try:
            # 显示进度
            progress_bar = progress_placeholder.progress(0)
            
            # 执行命令
            start_time = time.time()
            
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                timeout=300  # 5分钟超时
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            progress_bar.progress(1.0)
            
            if result.returncode != 0:
                st.error("❌ 查询失败")
                st.code(result.stderr)
            else:
                st.success(f"✅ 查询完成 (耗时 {execution_time:.1f}秒)")
                
                # 解析结果
                data = []
                output_lines = result.stdout.splitlines()
                
                for line in output_lines:
                    parsed = parse_run_output_line(line)
                    if parsed:
                        script, title, link, status = parsed
                        data.append({
                            'script': script,
                            'title': title,
                            'link': link,
                            'status': status
                        })
                
                if not data:
                    st.warning("⚠️ 没有解析到数据")
                    with st.expander("🔍 原始输出"):
                        st.code(result.stdout)
                else:
                    df = pd.DataFrame(data)
                    
                    # 统计
                    total = len(df)
                    success = len(df[df['status'] == 'success'])
                    no_match = len(df[df['status'] == 'no_match'])
                    error = len(df[df['status'].isin(['error', 'timeout'])])
                    
                    # 显示统计
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("✅ 成功", success)
                    with col2:
                        st.metric("⚠️ 无匹配", no_match)
                    with col3:
                        st.metric("❌ 错误", error)
                    with col4:
                        st.metric("总数", total)
                    
                    # 筛选选项
                    show_filter = st.selectbox(
                        "显示筛选:",
                        ["仅成功", "全部", "仅错误"],
                        index=0
                    )
                    
                    # 应用筛选
                    if show_filter == "仅成功":
                        filtered_df = df[df['status'] == 'success']
                    elif show_filter == "仅错误":
                        filtered_df = df[df['status'].isin(['error', 'timeout'])]
                    else:
                        filtered_df = df.copy()
                    
                    # 显示结果
                    if len(filtered_df) > 0:
                        # 准备显示数据
                        display_df = filtered_df.copy()
                        
                        # 状态符号
                        status_map = {
                            'success': '✅',
                            'no_match': '⚠️',
                            'empty': '📝',
                            'error': '❌',
                            'timeout': '⏰'
                        }
                        display_df['状态'] = display_df['status'].map(status_map)
                        
                        # 选择要显示的列
                        display_cols = ['script', 'title', 'link', '状态']
                        display_df = display_df[display_cols].rename(columns={
                            'script': '数据源',
                            'title': '标题',
                            'link': '链接'
                        })
                        
                        st.dataframe(
                            display_df,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "链接": st.column_config.LinkColumn("链接")
                            }
                        )
                        
                        # 下载按钮
                        csv_data = filtered_df[['script', 'title', 'link']].to_csv(index=False, encoding='utf-8')
                        st.download_button(
                            "📥 下载 CSV",
                            csv_data.encode('utf-8'),
                            f"海事舆情_{date_str}.csv",
                            "text/csv"
                        )
                    else:
                        st.info("ℹ️ 当前筛选条件下无结果")
                
                # 显示原始输出（调试用）
                with st.expander("📄 原始输出"):
                    st.text("标准输出:")
                    st.code(result.stdout)
                    if result.stderr:
                        st.text("错误输出:")
                        st.code(result.stderr)
        
        except subprocess.TimeoutExpired:
            st.error("❌ 查询超时（5分钟）")
        except Exception as e:
            st.error(f"❌ 发生错误: {str(e)}")

# 侧边栏
with st.sidebar:
    st.markdown("### ⚡ 简化版")
    st.markdown("""
    **特点:**
    - 🎯 简化界面，稳定可靠
    - 🚀 快速模式：跳过慢脚本
    - 📊 清晰的结果展示
    - 📥 CSV下载功能
    
    **模式说明:**
    - 🚀 快速模式：1-2分钟，跳过问题脚本
    - 🔧 完整模式：2-4分钟，处理所有脚本
    """)
    
    if st.button("🔄 刷新页面"):
        st.experimental_rerun()
