# app.py - 加速优化版
import streamlit as st
import subprocess
import sys
import pandas as pd
import datetime
from pathlib import Path
import os
import time

# 页面配置
st.set_page_config(
    page_title="海事舆情每日监测平台", 
    page_icon="📅",
    layout="wide"
)

st.title("📅 海事舆情每日监测平台")
st.markdown("---")

# 初始化状态
if 'debug_logs' not in st.session_state:
    st.session_state.debug_logs = []

def add_log(message, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {level}: {message}"
    st.session_state.debug_logs.append(log_entry)

def parse_run_output_line(line):
    """解析run.py的输出行"""
    line = line.strip()
    
    # 处理错误信息
    if line.startswith("[Error] 调用") and "失败" in line:
        try:
            script_part = line.split("调用")[1].split("失败")[0].strip()
            return (script_part, "", "", "error")
        except:
            return ("未知脚本", "", "", "error")
    
    # 处理超时信息
    if line.startswith("[Error] 调用") and "超时" in line:
        try:
            script_part = line.split("调用")[1].split("超时")[0].strip()
            return (script_part, "", "", "timeout")
        except:
            return ("未知脚本", "", "", "timeout")
    
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

# 快速环境检查
def quick_check_environment():
    run_py_exists = Path("run.py").exists()
    scripts = [
        "中国外交部.py", "国际海事组织.py", "世界贸易组织.py", "日本外务省.py", 
        "联合国海洋法庭.py", "国际海底管理局.py", "战略与国际研究中心.py", 
        "美国国务院.py", "美国运输部海事管理局.py", "中国海事局.py", 
        "日本海上保安大学校.py", "日本海上保安厅.py", "太平洋岛国论坛.py", 
        "越南外交部.py", "越南外交学院.py"
    ]
    
    existing_count = sum(1 for script in scripts if Path(script).exists())
    
    return run_py_exists, existing_count, len(scripts)

# 快速环境检查
run_py_ok, existing_scripts, total_scripts = quick_check_environment()

if not run_py_ok:
    st.error("❌ 找不到 run.py 文件")
    st.stop()

with st.expander("🔍 环境状态", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        st.metric("run.py", "✅ 存在" if run_py_ok else "❌ 缺失")
    with col2:
        st.metric("爬虫脚本", f"{existing_scripts}/{total_scripts}")

# 主界面
st.markdown("### 📅 查询设置")

col1, col2 = st.columns([2, 1])

with col1:
    date_input = st.date_input(
        "选择查询日期:",
        value=datetime.date.today()
    )

with col2:
    run_mode = st.selectbox(
        "运行模式:",
        ["🚀 快速模式（跳过慢脚本）", "🔧 完整模式（处理所有脚本）"],
        index=0,
        help="快速模式跳过经常出错的日本脚本，1-2分钟完成"
    )
    fast_mode = "快速模式" in run_mode
    
    st.write("")
    query_button = st.button("🔍 开始查询", type="primary", use_container_width=True)

# 查询逻辑
if query_button:
    st.session_state.debug_logs = []
    
    date_str = date_input.strftime("%Y-%m-%d")
    add_log(f"开始查询日期: {date_str}, 模式: {'快速' if fast_mode else '完整'}", "INFO")
    
    # 状态显示
    status_container = st.container()
    progress_container = st.container()
    
    with status_container:
        status_text = st.empty()
        progress_bar = st.progress(0)
    
    # 简化日志显示
    log_container = st.container()
    
    # 构建命令
    command = [sys.executable, "run.py", "--date", date_str]
    if fast_mode:
        command.append("--fast")
    
    add_log(f"执行命令: {' '.join(command)}", "INFO")
    
    try:
        status_text.info("🔄 启动查询进程...")
        start_time = time.time()
        
        # 简化版实时监控
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            universal_newlines=True
        )
        
        stdout_lines = []
        stderr_lines = []
        script_count = 0
        last_script = ""
        
        # 实时读取（但减少界面更新频率）
        expected_scripts = 12 if fast_mode else 15  # 快速模式跳过3个慢脚本
        while process.poll() is None:
            try:
                # 读取标准输出
                line = process.stdout.readline()
                if line:
                    line = line.strip()
                    stdout_lines.append(line)
                    
                    # 检测脚本进度
                    if "[INFO] 开始处理脚本:" in line or "[INFO] 进度" in line:
                        script_count += 1
                        if "进度" in line:
                            # 从 "[INFO] 进度 X/Y: 脚本名" 中提取信息
                            try:
                                progress_part = line.split("进度")[1].split(":")[0].strip()
                                current, total = progress_part.split("/")
                                script_count = int(current)
                                expected_scripts = int(total)
                            except:
                                pass
                        
                        last_script = line.split(":")[-1].strip()
                        status_text.info(f"🔄 正在处理第 {script_count}/{expected_scripts} 个脚本: {last_script}")
                        progress_bar.progress(min(0.9, script_count / expected_scripts))
                    
                    # 检测完成
                    elif "▶" in line:
                        add_log(f"获得结果: {line[:50]}...", "DEBUG")
                
                # 读取错误输出
                err_line = process.stderr.readline()
                if err_line:
                    err_line = err_line.strip()
                    stderr_lines.append(err_line)
                    if "[Error]" in err_line:
                        add_log(f"脚本错误: {err_line[:50]}...", "WARNING")
                
                # 检查超时（总体超时8分钟）
                if time.time() - start_time > 480:
                    add_log("查询总体超时，终止进程", "ERROR")
                    process.terminate()
                    break
                    
            except:
                continue
        
        # 等待进程结束
        return_code = process.wait()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        add_log(f"执行完成，耗时: {execution_time:.1f}秒", "INFO")
        
        progress_bar.progress(1.0)
        
        # 处理结果
        if return_code != 0:
            status_text.error("❌ 查询失败")
            st.error("❌ 查询过程出现错误")
            
            if stderr_lines:
                with st.expander("🔍 错误信息"):
                    st.code('\n'.join(stderr_lines[-10:]))  # 只显示最后10行错误
        else:
            status_text.success(f"✅ 查询完成 (耗时 {execution_time:.1f}秒)")
            
            # 快速解析结果
            data = []
            for line in stdout_lines:
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
                st.warning("⚠️ 没有解析到任何数据")
                with st.expander("🔍 原始输出"):
                    st.code('\n'.join(stdout_lines[-20:]))  # 只显示最后20行
            else:
                df = pd.DataFrame(data)
                
                # 快速统计
                total = len(df)
                success = len(df[df['status'] == 'success'])
                no_match = len(df[df['status'] == 'no_match'])
                error = len(df[df['status'].isin(['error', 'timeout'])])
                
                # 结果展示
                st.markdown("### 📊 查询结果")
                
                # 紧凑的统计显示
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                with metric_col1:
                    st.metric("✅ 成功", success)
                with metric_col2:
                    st.metric("⚠️ 无匹配", no_match)
                with metric_col3:
                    st.metric("❌ 错误", error)
                with metric_col4:
                    st.metric("⏱️ 耗时", f"{execution_time:.1f}s")
                
                # 如果有错误，简单显示
                if error > 0:
                    error_scripts = df[df['status'].isin(['error', 'timeout'])]['script'].tolist()
                    st.warning(f"⚠️ {error} 个脚本异常: {', '.join(error_scripts)}")
                
                # 简化的筛选
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
                
                # 显示结果表格
                if len(filtered_df) > 0:
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
                    
                    # 重命名并选择列
                    display_df = display_df[['script', 'title', 'link', '状态']].rename(columns={
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
                    
                    # 下载
                    col1, col2 = st.columns(2)
                    with col1:
                        csv_data = filtered_df[['script', 'title', 'link']].to_csv(index=False, encoding='utf-8')
                        st.download_button(
                            "📥 下载 CSV",
                            csv_data.encode('utf-8'),
                            f"海事舆情_{date_str}.csv",
                            "text/csv",
                            use_container_width=True
                        )
                    
                    with col2:
                        # 简单统计下载
                        summary = f"查询日期: {date_str}\n"
                        summary += f"总数据源: {total}\n"
                        summary += f"成功获取: {success}\n"
                        summary += f"无匹配: {no_match}\n"
                        summary += f"错误: {error}\n"
                        summary += f"查询耗时: {execution_time:.1f}秒\n\n"
                        
                        for _, row in filtered_df.iterrows():
                            if row['status'] == 'success':
                                summary += f"{row['script']}: {row['title']}\n{row['link']}\n\n"
                        
                        st.download_button(
                            "📥 下载报告",
                            summary.encode('utf-8'),
                            f"海事舆情报告_{date_str}.txt",
                            "text/plain",
                            use_container_width=True
                        )
                else:
                    st.info("ℹ️ 当前筛选条件下无结果")
        
        # 简化的日志显示
        with log_container:
            with st.expander(f"📄 执行日志 ({len(st.session_state.debug_logs)} 条)", expanded=False):
                if st.session_state.debug_logs:
                    # 只显示最重要的日志
                    important_logs = [log for log in st.session_state.debug_logs 
                                    if "WARNING" in log or "ERROR" in log or "开始" in log or "完成" in log]
                    st.text_area("", "\n".join(important_logs[-10:]), height=200)
        
    except Exception as e:
        status_text.error("❌ 查询异常")
        st.error(f"❌ 发生错误: {str(e)}")
        add_log(f"异常: {str(e)}", "ERROR")

# 简化的侧边栏
with st.sidebar:
    st.markdown("### ⚡ 智能优化版")
    st.markdown("""
    **核心优化:**
    - 🎯 **智能分类**：快/中/慢脚本分别处理
    - ⚡ **快速模式**：跳过经常出错的慢脚本
    - ⏱️ **差异化超时**：慢脚本15秒快速跳过
    - 📊 **优先处理**：先处理快速稳定的脚本
    
    **时间预期:**
    - 🚀 快速模式：1-2分钟（12个脚本）
    - 🔧 完整模式：2-4分钟（15个脚本）
    
    **跳过的脚本:**
    - 日本外务省（经常崩溃）
    - 日本海上保安大学校（网络慢）
    - 日本海上保安厅（驱动问题）
    """)
    
    st.markdown(f"### 📊 环境状态")
    st.markdown(f"- run.py: {'✅' if run_py_ok else '❌'}")
    st.markdown(f"- 脚本: {existing_scripts}/{total_scripts}")
    
    if st.button("🔄 刷新状态"):
        st.experimental_rerun()
