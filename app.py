# app.py
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
    print(log_entry)


def parse_run_output_line(line):
    """
    解析run.py的输出行
    输入格式：脚本名 ▶ 标题  链接
    或：脚本名 ▶ ✖ 没有找到包含 '日期' 的记录
    返回：(script, title, link, status)
    """
    line = line.strip()

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
    # 内容格式：标题  链接
    # 链接通常以http开头
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

    # 确定状态
    if title or link:
        status = "success"
    else:
        status = "empty"

    return (script, title, link, status)


# 环境检查
def check_environment():
    add_log("开始环境检查", "INFO")

    # 检查run.py
    run_py_path = Path("run.py")
    if run_py_path.exists():
        add_log("✅ run.py 文件存在", "SUCCESS")
    else:
        add_log("❌ run.py 文件不存在", "ERROR")
        return False

    # 检查爬虫脚本
    scripts = [
        "中国外交部.py", "国际海事组织.py", "世界贸易组织.py", "日本外务省.py",
        "联合国海洋法庭.py", "国际海底管理局.py", "战略与国际研究中心.py",
        "美国国务院.py", "美国运输部海事管理局.py", "中国海事局.py",
        "日本海上保安大学校.py", "日本海上保安厅.py", "太平洋岛国论坛.py",
        "越南外交部.py", "越南外交学院.py"
    ]

    existing_count = 0
    for script in scripts:
        if Path(script).exists():
            existing_count += 1
            add_log(f"✅ {script} 存在", "SUCCESS")
        else:
            add_log(f"❌ {script} 不存在", "WARNING")

    add_log(f"脚本检查完成: {existing_count}/{len(scripts)} 个存在", "INFO")
    return True


# 运行环境检查
with st.expander("🔍 环境检查", expanded=True):
    env_placeholder = st.empty()

    if check_environment():
        with env_placeholder.container():
            st.success("✅ 环境检查通过")
            if st.session_state.debug_logs:
                st.text_area("检查日志:", "\n".join(st.session_state.debug_logs[-10:]), height=150)
    else:
        with env_placeholder.container():
            st.error("❌ 环境检查失败")
            if st.session_state.debug_logs:
                st.text_area("检查日志:", "\n".join(st.session_state.debug_logs), height=200)
        st.stop()

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
    # 清空之前的日志
    st.session_state.debug_logs = []

    date_str = date_input.strftime("%Y-%m-%d")
    add_log(f"开始查询日期: {date_str}", "INFO")

    # 状态显示
    status_placeholder = st.empty()
    progress_placeholder = st.empty()
    log_placeholder = st.empty()


    def update_logs():
        with log_placeholder.container():
            with st.expander("📄 执行日志", expanded=True):
                st.text_area("", "\n".join(st.session_state.debug_logs[-15:]), height=250,
                             key=f"logs_{len(st.session_state.debug_logs)}")


    # 构建命令（绝对不使用--json参数）
    command = [sys.executable, "run.py", "--date", date_str]
    add_log(f"构建命令: {' '.join(command)}", "INFO")
    update_logs()

    try:
        progress_bar = progress_placeholder.progress(0)
        status_placeholder.info("🔄 正在查询，请稍候...")

        add_log("开始执行命令", "INFO")
        update_logs()

        start_time = time.time()

        # 使用实时输出监控
        import threading
        from queue import Queue


        def read_output(pipe, queue, prefix):
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
            cwd=os.getcwd(),
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

        # 实时读取输出
        stdout_lines = []
        stderr_lines = []
        last_update = time.time()

        while process.poll() is None or not output_queue.empty():
            try:
                # 从队列读取输出
                prefix, line = output_queue.get(timeout=1)

                if prefix == "OUT":
                    stdout_lines.append(line)
                    add_log(f"实时输出: {line}", "DEBUG")
                elif prefix == "ERR":
                    stderr_lines.append(line)
                    add_log(f"错误输出: {line}", "WARNING")

                # 每2秒更新一次界面
                if time.time() - last_update > 2:
                    update_logs()
                    # 根据输出行数更新进度
                    progress = min(0.9, len(stdout_lines) * 0.03 + 0.1)
                    progress_bar.progress(progress)
                    last_update = time.time()

            except:
                # 检查超时
                if time.time() - start_time > 300:  # 5分钟超时
                    add_log("执行超时，终止进程", "ERROR")
                    process.terminate()
                    break
                continue

        # 等待进程结束
        return_code = process.wait()


        # 模拟原来的返回结果
        class ProcessResult:
            def __init__(self, returncode, stdout_lines, stderr_lines):
                self.returncode = returncode
                self.stdout = '\n'.join(stdout_lines)
                self.stderr = '\n'.join(stderr_lines)


        process = ProcessResult(return_code, stdout_lines, stderr_lines)

        end_time = time.time()
        execution_time = end_time - start_time

        add_log(f"命令执行完成，耗时: {execution_time:.2f}秒", "INFO")
        add_log(f"返回码: {process.returncode}", "INFO")

        progress_bar.progress(0.5)
        update_logs()

        # 检查执行结果
        if process.returncode != 0:
            add_log("命令执行失败", "ERROR")
            add_log(f"错误信息: {process.stderr.strip()}", "ERROR")

            status_placeholder.error("❌ 查询失败")
            st.error("❌ 查询失败")
            st.code(process.stderr.strip())

            with st.expander("🔍 调试信息"):
                st.text("标准输出:")
                st.code(process.stdout if process.stdout else "无输出")
                st.text("错误输出:")
                st.code(process.stderr if process.stderr else "无错误")
        else:
            add_log("命令执行成功，开始解析输出", "SUCCESS")

            # 解析输出
            output_lines = process.stdout.splitlines()
            add_log(f"输出共 {len(output_lines)} 行", "INFO")

            data = []
            for i, line in enumerate(output_lines):
                line = line.strip()
                if not line:
                    continue

                # 跳过不相关的行
                if line.startswith("✅") or line.startswith("[Error]") or "已将结果导出到" in line:
                    add_log(f"跳过状态行: {line[:50]}...", "DEBUG")
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
                    add_log(f"解析成功: {script} -> {status}", "SUCCESS")
                else:
                    add_log(f"无法解析: {line[:50]}...", "WARNING")

            progress_bar.progress(0.8)
            update_logs()

            add_log(f"解析完成，获得 {len(data)} 条记录", "SUCCESS")

            if not data:
                status_placeholder.warning("⚠️ 没有解析到任何数据")

                with st.expander("🔍 原始输出（调试用）"):
                    st.text("完整输出:")
                    st.code(process.stdout)
                    st.text("逐行分析:")
                    for i, line in enumerate(output_lines[:20]):
                        st.text(f"第{i + 1}行: {repr(line)}")
            else:
                # 创建DataFrame
                df = pd.DataFrame(data)

                # 统计
                total = len(df)
                success = len(df[df['status'] == 'success'])
                no_match = len(df[df['status'] == 'no_match'])
                empty = len(df[df['status'] == 'empty'])

                add_log(f"统计: 总数{total}, 成功{success}, 无匹配{no_match}, 空{empty}", "INFO")

                status_placeholder.success(f"✅ 查询完成！获得 {success} 条有效记录")
                progress_bar.progress(1.0)

                # 显示统计
                st.markdown("### 📊 查询结果统计")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("总数据源", total)
                with col2:
                    st.metric("成功获取", success)
                with col3:
                    st.metric("无匹配记录", no_match)
                with col4:
                    st.metric("其他状态", empty)

                st.markdown("---")

                # 筛选选项
                filter_col1, filter_col2 = st.columns(2)
                with filter_col1:
                    show_filter = st.selectbox(
                        "显示筛选:",
                        ["全部", "仅成功", "仅无匹配", "仅空记录"],
                        index=0
                    )
                with filter_col2:
                    show_empty_titles = st.checkbox("显示空标题", value=True)

                # 应用筛选
                filtered_df = df.copy()

                if show_filter == "仅成功":
                    filtered_df = filtered_df[filtered_df['status'] == 'success']
                elif show_filter == "仅无匹配":
                    filtered_df = filtered_df[filtered_df['status'] == 'no_match']
                elif show_filter == "仅空记录":
                    filtered_df = filtered_df[filtered_df['status'] == 'empty']

                if not show_empty_titles:
                    filtered_df = filtered_df[filtered_df['title'].str.strip() != '']

                # 显示数据
                if len(filtered_df) > 0:
                    # 准备显示数据
                    display_df = filtered_df.copy()

                    # 状态中文化
                    status_map = {
                        'success': '✅ 成功',
                        'no_match': '⚠️ 无匹配',
                        'empty': '📝 空结果'
                    }
                    display_df['status_cn'] = display_df['status'].map(status_map)

                    # 重新排列列
                    display_df = display_df[['script', 'title', 'link', 'status_cn']].rename(columns={
                        'script': '数据源',
                        'title': '标题',
                        'link': '链接',
                        'status_cn': '状态'
                    })

                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "链接": st.column_config.LinkColumn("链接"),
                        }
                    )

                    # 下载按钮
                    st.markdown("---")
                    download_col1, download_col2 = st.columns(2)

                    with download_col1:
                        csv_data = filtered_df.drop('status', axis=1).to_csv(index=False, encoding='utf-8')
                        st.download_button(
                            label="📥 下载 CSV",
                            data=csv_data.encode('utf-8'),
                            file_name=f"海事舆情_{date_str}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

                    with download_col2:
                        # 简单的文本格式下载
                        text_data = ""
                        for _, row in filtered_df.iterrows():
                            if row['title'] and row['link']:
                                text_data += f"{row['script']}: {row['title']} - {row['link']}\n"

                        st.download_button(
                            label="📥 下载 TXT",
                            data=text_data.encode('utf-8'),
                            file_name=f"海事舆情_{date_str}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                else:
                    st.info("ℹ️ 根据筛选条件，没有找到匹配的记录")

        update_logs()

    except subprocess.TimeoutExpired:
        add_log("查询超时", "ERROR")
        status_placeholder.error("❌ 查询超时")
        st.error("❌ 查询超时（超过5分钟）")
        update_logs()
    except Exception as e:
        add_log(f"发生异常: {str(e)}", "ERROR")
        status_placeholder.error("❌ 查询异常")
        st.error(f"❌ 查询过程中发生错误: {str(e)}")
        update_logs()

# 侧边栏
with st.sidebar:
    st.markdown("### 📋 使用指南")
    st.markdown("""
    1. 🗓️ 选择查询日期
    2. 🔍 点击开始查询
    3. ⏳ 等待执行完成
    4. 📊 查看结果统计
    5. 📥 下载数据文件
    """)

    st.markdown("### 📊 数据源")
    scripts_info = [
        "中国外交部", "国际海事组织", "世界贸易组织",
        "日本外务省", "联合国海洋法庭", "国际海底管理局",
        "战略与国际研究中心", "美国国务院", "美国运输部海事管理局",
        "中国海事局", "日本海上保安大学校", "日本海上保安厅",
        "太平洋岛国论坛", "越南外交部", "越南外交学院"
    ]

    for script in scripts_info:
        st.text(f"• {script}")

    st.markdown("### ⚠️ 注意事项")
    st.markdown("""
    - 查询时间：1-5分钟
    - 需要网络连接
    - 部分源可能暂时不可用
    - 查看日志了解详情
    """)


