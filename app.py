# app.py
import streamlit as st
import subprocess
import sys
import pandas as pd
import datetime
import json
from pathlib import Path
import os
import time

# 页面配置
st.set_page_config(
    page_title="海事舆情每日监测平台", 
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("📅 海事舆情每日监测平台")
st.markdown("---")

# 调试信息容器
debug_container = st.container()

# 创建日志记录函数
def log_message(message, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    return f"[{timestamp}] {level}: {message}"

# 初始化状态
if 'debug_logs' not in st.session_state:
    st.session_state.debug_logs = []

def add_log(message, level="INFO"):
    log_entry = log_message(message, level)
    st.session_state.debug_logs.append(log_entry)
    print(log_entry)  # 同时输出到控制台

# 环境检查函数
def check_environment():
    add_log("开始环境检查", "INFO")
    
    # 检查Python版本
    python_version = sys.version
    add_log(f"Python版本: {python_version}", "INFO")
    
    # 检查当前工作目录
    current_dir = os.getcwd()
    add_log(f"当前工作目录: {current_dir}", "INFO")
    
    # 检查 run.py 文件
    run_py_path = Path("run.py")
    if run_py_path.exists():
        add_log("✅ run.py 文件存在", "SUCCESS")
        add_log(f"run.py 文件大小: {run_py_path.stat().st_size} bytes", "INFO")
    else:
        add_log("❌ run.py 文件不存在", "ERROR")
        return False
    
    # 检查爬虫脚本文件
    scripts = [
        "中国外交部.py", "国际海事组织.py", "世界贸易组织.py", "日本外务省.py", "联合国海洋法庭.py", "国际海底管理局.py",
        "战略与国际研究中心.py", "美国国务院.py", "美国运输部海事管理局.py", "中国海事局.py", "日本海上保安大学校.py",
        "日本海上保安厅.py", "太平洋岛国论坛.py", "越南外交部.py", "越南外交学院.py"
    ]
    
    existing_scripts = []
    missing_scripts = []
    
    for script in scripts:
        script_path = Path(script)
        if script_path.exists():
            existing_scripts.append(script)
            size = script_path.stat().st_size
            add_log(f"✅ {script} 存在 ({size} bytes)", "SUCCESS")
        else:
            missing_scripts.append(script)
            add_log(f"❌ {script} 不存在", "WARNING")
    
    add_log(f"脚本检查完成: {len(existing_scripts)} 个存在, {len(missing_scripts)} 个缺失", "INFO")
    
    # 检查系统命令
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        add_log(f"Python可执行文件测试: {result.stdout.strip()}", "SUCCESS")
    except Exception as e:
        add_log(f"Python可执行文件测试失败: {str(e)}", "ERROR")
        return False
    
    return True

# 运行环境检查
with debug_container:
    with st.expander("🔍 环境检查日志", expanded=True):
        env_check_placeholder = st.empty()
        
        if check_environment():
            env_status = "✅ 环境检查通过"
        else:
            env_status = "❌ 环境检查失败"
        
        with env_check_placeholder.container():
            st.text(env_status)
            if st.session_state.debug_logs:
                st.text_area("检查日志:", "\n".join(st.session_state.debug_logs), height=200)

# 只有在环境检查通过时才显示主界面
run_py_path = Path("run.py")
if not run_py_path.exists():
    st.error("❌ 找不到 run.py 文件，请确保文件在同一目录下")
    st.stop()

# 创建两列布局
col1, col2 = st.columns([2, 1])

with col1:
    # 日期输入 - 使用日期选择器
    date_input = st.date_input(
        "请选择查询日期:",
        value=datetime.date.today(),
        help="选择要查询的日期"
    )

with col2:
    # 查询按钮
    st.write("")  # 添加一些空白对齐
    st.write("")
    query_button = st.button("🔍 开始查询", type="primary", use_container_width=True)

# 查询逻辑
if query_button:
    # 清空之前的日志
    st.session_state.debug_logs = []
    
    date_str = date_input.strftime("%Y-%m-%d")
    add_log(f"开始查询日期: {date_str}", "INFO")
    
    # 创建实时日志显示区域
    log_placeholder = st.empty()
    status_placeholder = st.empty()
    progress_placeholder = st.empty()
    
    def update_log_display():
        with log_placeholder.container():
            st.text_area("🔄 实时执行日志:", "\n".join(st.session_state.debug_logs[-20:]), height=300, key=f"log_{len(st.session_state.debug_logs)}")
    
    add_log("准备执行查询命令", "INFO")
    update_log_display()
    
    # 构建命令
    cmd = [sys.executable, "run.py", "--date", date_str, "--json"]
    add_log(f"执行命令: {' '.join(cmd)}", "INFO")
    update_log_display()
    
    try:
        # 显示进度条
        progress_bar = progress_placeholder.progress(0)
        status_placeholder.info("🔄 正在启动查询进程...")
        
        add_log("开始执行subprocess.run", "INFO")
        update_log_display()
        
        start_time = time.time()
        
        # 执行命令
        proc = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            encoding="utf-8",
            cwd=os.getcwd(),
            timeout=300
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        add_log(f"命令执行完成，耗时: {execution_time:.2f} 秒", "INFO")
        add_log(f"返回码: {proc.returncode}", "INFO")
        
        # 记录原始输出
        add_log(f"标准输出长度: {len(proc.stdout)} 字符", "INFO")
        add_log(f"错误输出长度: {len(proc.stderr)} 字符", "INFO")
        
        update_log_display()
        progress_bar.progress(0.5)
        
        # 显示原始输出内容（截取前1000字符用于调试）
        if proc.stdout:
            stdout_preview = proc.stdout[:1000] + ("..." if len(proc.stdout) > 1000 else "")
            add_log(f"标准输出预览: {stdout_preview}", "DEBUG")
        
        if proc.stderr:
            stderr_preview = proc.stderr[:1000] + ("..." if len(proc.stderr) > 1000 else "")
            add_log(f"错误输出预览: {stderr_preview}", "DEBUG")
        
        update_log_display()
        
        # 检查是否成功执行
        if proc.returncode != 0:
            add_log("进程返回非零状态码，执行失败", "ERROR")
            status_placeholder.error(f"❌ 查询失败 (返回码: {proc.returncode})")
            
            st.error(f"❌ 查询失败:")
            
            # 显示详细错误信息
            if proc.stderr.strip():
                st.code(proc.stderr.strip())
                add_log(f"错误详情: {proc.stderr.strip()}", "ERROR")
            
            # 显示完整的调试信息
            with st.expander("🔍 完整调试信息"):
                st.text("完整标准输出:")
                st.code(proc.stdout if proc.stdout else "无输出")
                st.text("完整错误输出:")
                st.code(proc.stderr if proc.stderr else "无错误")
                st.text("执行日志:")
                st.text_area("", "\n".join(st.session_state.debug_logs), height=400)
        else:
            add_log("进程执行成功，开始解析输出", "SUCCESS")
            status_placeholder.success("✅ 查询进程执行成功")
            progress_bar.progress(0.7)
            update_log_display()
            
            try:
                # 尝试解析 JSON 输出
                add_log("开始解析JSON输出", "INFO")
                
                # 清理输出（移除可能的额外输出）
                stdout_clean = proc.stdout.strip()
                
                # 寻找JSON部分
                json_start = stdout_clean.find('[')
                json_end = stdout_clean.rfind(']') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = stdout_clean[json_start:json_end]
                    add_log(f"提取JSON字符串长度: {len(json_str)}", "INFO")
                    add_log(f"JSON预览: {json_str[:200]}...", "DEBUG")
                else:
                    add_log("未找到有效的JSON格式输出", "ERROR")
                    raise ValueError("输出中未找到JSON格式数据")
                
                update_log_display()
                
                data = json.loads(json_str)
                add_log(f"JSON解析成功，获得 {len(data)} 条记录", "SUCCESS")
                
                progress_bar.progress(0.9)
                update_log_display()
                
                if not data:
                    add_log("解析结果为空", "WARNING")
                    status_placeholder.warning("⚠️ 没有找到任何数据")
                else:
                    # 转换为 DataFrame
                    df = pd.DataFrame(data)
                    add_log(f"创建DataFrame成功，shape: {df.shape}", "SUCCESS")
                    
                    # 统计信息
                    total_scripts = len(df)
                    success_count = len(df[df['status'] == 'success'])
                    error_count = len(df[df['status'] == 'error'])
                    no_match_count = len(df[df['status'] == 'no_match'])
                    
                    add_log(f"统计结果 - 总计:{total_scripts}, 成功:{success_count}, 错误:{error_count}, 无匹配:{no_match_count}", "INFO")
                    
                    # 显示统计信息
                    status_placeholder.success(f"✅ 查询完成！处理了 {total_scripts} 个数据源")
                    progress_bar.progress(1.0)
                    
                    # 创建指标展示
                    st.markdown("### 📊 执行结果统计")
                    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                    
                    with metric_col1:
                        st.metric("总脚本数", total_scripts)
                    with metric_col2:
                        st.metric("成功获取", success_count, delta=f"{success_count}/{total_scripts}")
                    with metric_col3:
                        st.metric("无匹配记录", no_match_count)
                    with metric_col4:
                        st.metric("错误数量", error_count, delta=f"-{error_count}" if error_count > 0 else "0")
                    
                    st.markdown("---")
                    
                    # 筛选选项
                    st.subheader("📋 查询结果")
                    
                    filter_col1, filter_col2 = st.columns(2)
                    
                    with filter_col1:
                        show_filter = st.selectbox(
                            "显示筛选:",
                            ["全部", "仅成功", "仅错误", "仅无匹配"],
                            index=0
                        )
                    
                    with filter_col2:
                        show_empty = st.checkbox("显示空标题记录", value=True)
                    
                    # 应用筛选
                    filtered_df = df.copy()
                    
                    if show_filter == "仅成功":
                        filtered_df = filtered_df[filtered_df['status'] == 'success']
                    elif show_filter == "仅错误":
                        filtered_df = filtered_df[filtered_df['status'] == 'error']
                    elif show_filter == "仅无匹配":
                        filtered_df = filtered_df[filtered_df['status'] == 'no_match']
                    
                    if not show_empty:
                        filtered_df = filtered_df[filtered_df['title'].str.strip() != '']
                    
                    add_log(f"应用筛选后显示 {len(filtered_df)} 条记录", "INFO")
                    
                    # 显示数据表格
                    if len(filtered_df) > 0:
                        # 创建显示用的DataFrame，添加链接格式化
                        display_df = filtered_df.copy()
                        
                        # 格式化链接列
                        def format_link(link):
                            if link and link.startswith('http'):
                                return f'<a href="{link}" target="_blank">🔗 链接</a>'
                            return link
                        
                        display_df['link'] = display_df['link'].apply(format_link)
                        
                        # 重命名列
                        display_df = display_df.rename(columns={
                            'script': '数据源',
                            'title': '标题',
                            'link': '链接',
                            'status': '状态'
                        })
                        
                        # 显示表格
                        st.dataframe(
                            display_df,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "链接": st.column_config.LinkColumn("链接"),
                                "状态": st.column_config.TextColumn(
                                    "状态",
                                    help="success: 成功获取数据, error: 脚本错误, no_match: 无匹配记录"
                                )
                            }
                        )
                        
                        # 下载功能
                        st.markdown("---")
                        download_col1, download_col2 = st.columns(2)
                        
                        with download_col1:
                            # CSV 下载
                            csv_data = filtered_df.drop('status', axis=1).to_csv(index=False, encoding='utf-8')
                            st.download_button(
                                label="📥 下载 CSV 文件",
                                data=csv_data.encode('utf-8'),
                                file_name=f"海事舆情_{date_str}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                        
                        with download_col2:
                            # JSON 下载
                            json_data = json.dumps(data, ensure_ascii=False, indent=2)
                            st.download_button(
                                label="📥 下载 JSON 文件",
                                data=json_data.encode('utf-8'),
                                file_name=f"海事舆情_{date_str}.json",
                                mime="application/json",
                                use_container_width=True
                            )
                    else:
                        st.info("ℹ️ 根据当前筛选条件，没有找到匹配的记录")
                        add_log("筛选后无匹配记录", "INFO")
                
                add_log("结果展示完成", "SUCCESS")
                
            except json.JSONDecodeError as e:
                add_log(f"JSON解析失败: {str(e)}", "ERROR")
                status_placeholder.error("❌ 解析结果失败")
                
                st.error(f"❌ 解析结果失败: {str(e)}")
                st.text("原始输出:")
                st.code(proc.stdout)
                
                # 尝试逐行解析，找出问题所在
                st.text("尝试逐行分析输出:")
                lines = proc.stdout.splitlines()
                for i, line in enumerate(lines[:20]):  # 只显示前20行
                    st.text(f"第{i+1}行: {repr(line)}")
            
            except Exception as e:
                add_log(f"处理结果时发生未知错误: {str(e)}", "ERROR")
                status_placeholder.error("❌ 处理结果时发生错误")
                
                st.error(f"❌ 处理结果时发生错误: {str(e)}")
                st.text("完整输出:")
                st.code(proc.stdout)
    
    except subprocess.TimeoutExpired:
        add_log("查询超时（超过5分钟）", "ERROR")
        status_placeholder.error("❌ 查询超时")
        st.error("❌ 查询超时（超过5分钟），请检查网络连接或减少查询范围")
    except Exception as e:
        add_log(f"执行过程中发生意外错误: {str(e)}", "ERROR")
        status_placeholder.error("❌ 执行失败")
        st.error(f"❌ 执行过程中发生错误: {str(e)}")
    
    # 显示完整的执行日志
    with st.expander("📄 完整执行日志", expanded=False):
        if st.session_state.debug_logs:
            st.text_area("详细日志:", "\n".join(st.session_state.debug_logs), height=500)
        else:
            st.text("无日志记录")

# 侧边栏信息
with st.sidebar:
    st.markdown("### 📋 使用说明")
    st.markdown("""
    1. 选择要查询的日期
    2. 点击"开始查询"按钮
    3. 等待系统爬取各个数据源
    4. 查看结果并可选择下载
    
    ### 📊 数据源包括:
    - 中国外交部
    - 国际海事组织
    - 世界贸易组织
    - 日本外务省
    - 联合国海洋法庭
    - 国际海底管理局
    - 战略与国际研究中心
    - 美国国务院
    - 美国运输部海事管理局
    - 中国海事局
    - 日本海上保安大学校
    - 日本海上保安厅
    - 太平洋岛国论坛
    - 越南外交部
    - 越南外交学院
    
    ### 🔧 调试功能:
    - 实时显示执行日志
    - 详细的错误信息
    - 环境检查功能
    - 原始输出查看
    
    ### ⚠️ 注意事项:
    - 查询可能需要几分钟时间
    - 确保网络连接正常
    - 部分数据源可能暂时无法访问
    - 查看执行日志了解详细进展
    """)
    
    if st.button("🔄 重新检查环境"):
        st.session_state.debug_logs = []
        st.experimental_rerun()
    
    st.markdown("---")
    st.markdown("### 📊 当前状态")
    if st.session_state.debug_logs:
        recent_logs = st.session_state.debug_logs[-5:]
        for log in recent_logs:
            st.text(log)
    else:
        st.text("暂无日志")
