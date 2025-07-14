# app.py - 简化可靠版
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

    # 显示查询状态
    status_placeholder = st.empty()
    progress_placeholder = st.empty()
    
    with status_placeholder.container():
        st.info("🔄 正在查询，请稍候...")
    
    with progress_placeholder.container():
        progress_bar = st.progress(0)
        progress_text = st.empty()
    
    # 构建命令
    command = [sys.executable, "run.py", "--date", date_str]

    try:
        start_time = time.time()
        
        # 更新进度
        progress_bar.progress(0.1)
        progress_text.text("正在启动查询进程...")
        
        # 执行命令（简化版本，不使用实时监控）
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            timeout=300  # 5分钟超时
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 完成进度
        progress_bar.progress(1.0)
        progress_text.text("✅ 查询完成")

        # 处理结果
        if result.returncode != 0:
            status_placeholder.error("❌ 查询失败")
            st.error("❌ 查询失败")
            if result.stderr:
                st.code(result.stderr.strip())
        else:
            status_placeholder.success(f"✅ 查询完成 (耗时 {execution_time:.1f}秒)")

            # 解析输出
            data = []
            output_lines = result.stdout.splitlines()
            
            for line in output_lines:
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

            if not data:
                st.warning("⚠️ 没有解析到任何数据")
                with st.expander("🔍 原始输出"):
                    st.code(result.stdout)
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

    except subprocess.TimeoutExpired:
        status_placeholder.error("❌ 查询超时")
        st.error("❌ 查询超时（超过5分钟）")
    except Exception as e:
        status_placeholder.error("❌ 查询异常")
        st.error(f"❌ 查询过程中发生错误: {str(e)}")
    finally:
        # 清理进度显示
        progress_placeholder.empty()

# 极简侧边栏
with st.sidebar:
    st.markdown("### ⚡ 功能特点")
    st.markdown("""
    - 🚀 智能进度显示
    - 📊 实时状态更新  
    - 🎯 结果筛选功能
    - 📥 多格式下载
    """)
    
    if st.button("🔄 刷新页面"):
        st.experimental_rerun()
