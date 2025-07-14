# app.py - 精简优化版
import streamlit as st
import subprocess
import sys
import pandas as pd
import datetime
from pathlib import Path
import time
import threading
from queue import Queue

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
        value=datetime.date.today(),
        help="选择要查询的日期"
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

    # 状态显示
    status_container = st.container()
    
    with status_container:
        status_text = st.empty()
        progress_container = st.empty()

    # 构建命令
    command = [sys.executable, "run.py", "--date", date_str]

    try:
        # 初始化进度
        with progress_container.container():
            progress_bar = st.progress(0)
            progress_text = st.empty()
        
        status_text.info("🔄 启动查询进程...")
        
        start_time = time.time()
        
        def read_output(pipe, queue, prefix):
            """读取输出的线程函数"""
            try:
                for line in iter(pipe.readline, ''):
                    if line.strip():
                        queue.put((prefix, line.strip()))
                pipe.close()
            except:
                pass

        # 启动进程
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            universal_newlines=True
        )

        # 创建队列和线程
        output_queue = Queue()
        stdout_thread = threading.Thread(target=read_output, args=(process.stdout, output_queue, "OUT"))
        stderr_thread = threading.Thread(target=read_output, args=(process.stderr, output_queue, "ERR"))

        stdout_thread.daemon = True
        stderr_thread.daemon = True
        stdout_thread.start()
        stderr_thread.start()

        # 实时读取输出并更新进度
        stdout_lines = []
        stderr_lines = []
        script_count = 0
        completed_scripts = 0
        current_script = ""
        total_scripts = 15  # 总脚本数
        
        while process.poll() is None or not output_queue.empty():
            try:
                prefix, line = output_queue.get(timeout=1)

                if prefix == "OUT":
                    stdout_lines.append(line)
                    
                    # 检测脚本开始
                    if "[INFO] 开始处理脚本:" in line:
                        script_count += 1
                        current_script = line.split(":")[-1].strip()
                        progress = (script_count - 1) / total_scripts
                        progress_bar.progress(progress)
                        progress_text.text(f"正在处理: {current_script} ({script_count}/{total_scripts})")
                        status_text.info(f"🔄 处理第 {script_count} 个脚本: {current_script}")
                    
                    # 检测脚本完成
                    elif "▶" in line or "[Error]" in line:
                        completed_scripts += 1
                        progress = completed_scripts / total_scripts
                        progress_bar.progress(min(progress, 0.95))
                        progress_text.text(f"已完成: {completed_scripts}/{total_scripts} 个脚本")
                    
                    # 检测进度信息
                    elif "[INFO] 进度" in line:
                        try:
                            # 从 "[INFO] 进度 X/Y: 脚本名" 中提取信息
                            progress_part = line.split("进度")[1].split(":")[0].strip()
                            current, total = progress_part.split("/")
                            script_count = int(current)
                            total_scripts = int(total)
                            current_script = line.split(":")[-1].strip()
                            
                            progress = (script_count - 1) / total_scripts
                            progress_bar.progress(progress)
                            progress_text.text(f"正在处理: {current_script} ({script_count}/{total_scripts})")
                            status_text.info(f"🔄 处理第 {script_count} 个脚本: {current_script}")
                        except:
                            pass

                elif prefix == "ERR":
                    stderr_lines.append(line)

            except:
                # 检查超时（5分钟）
                if time.time() - start_time > 300:
                    process.terminate()
                    status_text.error("❌ 查询超时")
                    st.error("❌ 查询超时（超过5分钟）")
                    st.stop()
                continue

        # 等待进程结束
        return_code = process.wait()
        
        # 完成进度
        progress_bar.progress(1.0)
        progress_text.text("✅ 查询完成")

        end_time = time.time()
        execution_time = end_time - start_time

        # 处理结果
        if return_code != 0:
            status_text.error("❌ 查询失败")
            st.error("❌ 查询失败")
            if stderr_lines:
                st.code('\n'.join(stderr_lines))
        else:
            status_text.success(f"✅ 查询完成 (耗时 {execution_time:.1f}秒)")

            # 解析输出
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
                    st.code('\n'.join(stdout_lines))
            else:
                df = pd.DataFrame(data)

                # 统计
                total = len(df)
                success = len(df[df['status'] == 'success'])
                no_match = len(df[df['status'] == 'no_match'])
                error = len(df[df['status'].isin(['error', 'timeout'])])
                empty = len(df[df['status'] == 'empty'])

                # 显示统计
                st.markdown("### 📊 查询结果统计")
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("总数据源", total)
                with col2:
                    st.metric("✅ 成功获取", success)
                with col3:
                    st.metric("⚠️ 无匹配记录", no_match)
                with col4:
                    st.metric("❌ 脚本错误", error)
                with col5:
                    st.metric("📝 其他状态", empty)

                # 如果有错误，显示简要信息
                if error > 0:
                    error_scripts = df[df['status'].isin(['error', 'timeout'])]['script'].tolist()
                    st.warning(f"⚠️ {error} 个脚本异常: {', '.join(error_scripts[:3])}{'...' if len(error_scripts) > 3 else ''}")

                st.markdown("---")

                # 筛选选项
                filter_col1, filter_col2 = st.columns(2)
                with filter_col1:
                    show_filter = st.selectbox(
                        "显示筛选:",
                        ["仅成功", "全部", "仅错误", "仅无匹配"],
                        index=0
                    )
                with filter_col2:
                    show_empty_titles = st.checkbox("显示空标题", value=True)

                # 应用筛选
                filtered_df = df.copy()

                if show_filter == "仅成功":
                    filtered_df = filtered_df[filtered_df['status'] == 'success']
                elif show_filter == "仅错误":
                    filtered_df = filtered_df[filtered_df['status'].isin(['error', 'timeout'])]
                elif show_filter == "仅无匹配":
                    filtered_df = filtered_df[filtered_df['status'] == 'no_match']

                if not show_empty_titles:
                    filtered_df = filtered_df[filtered_df['title'].str.strip() != '']

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
                        hide_index=True,
                        column_config={
                            "链接": st.column_config.LinkColumn("链接")
                        }
                    )

                    # 下载按钮
                    st.markdown("---")
                    download_col1, download_col2 = st.columns(2)

                    with download_col1:
                        csv_data = filtered_df[['script', 'title', 'link']].to_csv(index=False, encoding='utf-8')
                        st.download_button(
                            label="📥 下载 CSV",
                            data=csv_data.encode('utf-8'),
                            file_name=f"海事舆情_{date_str}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

                    with download_col2:
                        # 简单的文本格式下载
                        text_data = f"海事舆情查询结果 - {date_str}\n"
                        text_data += f"查询时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        text_data += f"总计: {total} 个数据源, 成功: {success} 个\n\n"
                        
                        for _, row in filtered_df.iterrows():
                            if row['status'] == 'success' and row['title'] and row['link']:
                                text_data += f"{row['script']}: {row['title']}\n{row['link']}\n\n"

                        st.download_button(
                            label="📥 下载 TXT",
                            data=text_data.encode('utf-8'),
                            file_name=f"海事舆情_{date_str}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                else:
                    st.info("ℹ️ 根据筛选条件，没有找到匹配的记录")

    except Exception as e:
        status_text.error("❌ 查询异常")
        st.error(f"❌ 查询过程中发生错误: {str(e)}")

# 简化的侧边栏
with st.sidebar:
    st.markdown("### 📊 数据源状态")
    
    # 快速检查文件状态
    scripts = [
        "中国外交部.py", "国际海事组织.py", "世界贸易组织.py", "日本外务省.py",
        "联合国海洋法庭.py", "国际海底管理局.py", "战略与国际研究中心.py",
        "美国国务院.py", "美国运输部海事管理局.py", "中国海事局.py",
        "日本海上保安大学校.py", "日本海上保安厅.py", "太平洋岛国论坛.py",
        "越南外交部.py", "越南外交学院.py"
    ]
    
    existing_count = sum(1 for script in scripts if Path(script).exists())
    run_py_exists = Path("run.py").exists()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("run.py", "✅" if run_py_exists else "❌")
    with col2:
        st.metric("脚本文件", f"{existing_count}/15")
    
    if existing_count < 15:
        st.warning(f"⚠️ 缺少 {15 - existing_count} 个脚本文件")
    
    st.markdown("---")
    st.markdown("### ⚡ 功能特点")
    st.markdown("""
    - 🚀 智能进度显示
    - 📊 实时状态更新  
    - 🎯 结果筛选功能
    - 📥 多格式下载
    """)
    
    if st.button("🔄 刷新页面"):
        st.experimental_rerun()
