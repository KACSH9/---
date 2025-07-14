# app.py
import streamlit as st
import subprocess
import sys
import pandas as pd
import datetime
import json
from pathlib import Path
import os

# 页面配置
st.set_page_config(
    page_title="海事舆情每日监测平台", 
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("📅 海事舆情每日监测平台")
st.markdown("---")

# 检查 run.py 是否存在
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
    date_str = date_input.strftime("%Y-%m-%d")
    
    with st.spinner("🔄 正在查询各个数据源，请稍候..."):
        # 构建命令
        cmd = [sys.executable, "run.py", "--date", date_str, "--json"]
        
        try:
            # 执行命令
            proc = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                encoding="utf-8",
                cwd=os.getcwd(),  # 确保在正确的工作目录
                timeout=300  # 5分钟超时
            )
            
            # 检查是否成功执行
            if proc.returncode != 0:
                st.error(f"❌ 查询失败:")
                st.code(proc.stderr.strip())
                
                # 显示详细错误信息
                with st.expander("🔍 详细错误信息"):
                    st.text("标准输出:")
                    st.code(proc.stdout)
                    st.text("错误输出:")
                    st.code(proc.stderr)
            else:
                try:
                    # 解析 JSON 输出
                    data = json.loads(proc.stdout.strip())
                    
                    if not data:
                        st.warning("⚠️ 没有找到任何数据")
                    else:
                        # 转换为 DataFrame
                        df = pd.DataFrame(data)
                        
                        # 统计信息
                        total_scripts = len(df)
                        success_count = len(df[df['status'] == 'success'])
                        error_count = len(df[df['status'] == 'error'])
                        no_match_count = len(df[df['status'] == 'no_match'])
                        
                        # 显示统计信息
                        st.success(f"✅ 查询完成！")
                        
                        # 创建指标展示
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
                        st.subheader("📊 查询结果")
                        
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
                        
                        # 显示数据表格
                        if len(filtered_df) > 0:
                            # 添加状态颜色标识
                            def highlight_status(row):
                                if row['status'] == 'success':
                                    return ['background-color: #d4edda'] * len(row)
                                elif row['status'] == 'error':
                                    return ['background-color: #f8d7da'] * len(row)
                                elif row['status'] == 'no_match':
                                    return ['background-color: #fff3cd'] * len(row)
                                return [''] * len(row)
                            
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
                        
                        # 详细日志
                        with st.expander("📄 查看详细运行日志"):
                            st.text("程序输出:")
                            if proc.stderr.strip():
                                st.code(proc.stderr.strip())
                            else:
                                st.text("无错误输出")
                
                except json.JSONDecodeError as e:
                    st.error(f"❌ 解析结果失败: {str(e)}")
                    st.text("原始输出:")
                    st.code(proc.stdout)
        
        except subprocess.TimeoutExpired:
            st.error("❌ 查询超时（超过5分钟），请检查网络连接或减少查询范围")
        except Exception as e:
            st.error(f"❌ 执行过程中发生错误: {str(e)}")

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
    
    ### ⚠️ 注意事项:
    - 查询可能需要几分钟时间
    - 确保网络连接正常
    - 部分数据源可能暂时无法访问
    """)
    
    st.markdown("---")
    st.markdown("### 🔧 技术支持")
    st.markdown("如遇问题请检查:")
    st.markdown("- run.py 文件是否存在")
    st.markdown("- 各爬虫脚本是否完整")
    st.markdown("- 网络连接是否正常")
