import streamlit as st
import subprocess
import sys
import pandas as pd
import datetime
import os
from pathlib import Path

st.set_page_config(page_title="海事舆情每日监测平台", page_icon="📅")
st.title("📅 海事舆情每日监测平台")

date_input = st.text_input("请选择查询日期：", value=str(datetime.date.today()))

if st.button("🔍 查询"):
    with st.spinner("查询中，请稍候..."):
        date_str = date_input.strip()
        
        # 获取当前脚本的目录
        current_dir = Path(__file__).parent.resolve()
        run_script_path = current_dir / "run.py"
        
        # 确保run.py存在
        if not run_script_path.exists():
            st.error(f"找不到 run.py 文件：{run_script_path}")
        else:
            # 在正确的目录下运行
            command = [sys.executable, str(run_script_path), "--date", date_str]
            
            # 添加调试信息
            with st.expander("🔧 调试信息", expanded=False):
                st.write(f"当前目录: {current_dir}")
                st.write(f"Run脚本路径: {run_script_path}")
                st.write(f"执行命令: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                cwd=str(current_dir)  # 设置工作目录
            )
            
            if result.returncode != 0:
                st.error(f"运行失败：{result.stderr.strip()}")
                # 显示详细错误信息
                with st.expander("❌ 错误详情"):
                    st.code(result.stderr)
            else:
                output = result.stdout
                
                # 显示原始输出（用于调试）
                with st.expander("📝 原始输出", expanded=False):
                    st.code(output)
                
                # 解析包含"▶"的行
                matched_lines = [
                    line for line in output.splitlines()
                    if "▶" in line and not line.startswith("[")  # 排除调试信息
                ]
                
                results = []
                for line in matched_lines:
                    try:
                        script, rest = line.split("▶", 1)
                        script = script.strip()
                        rest = rest.strip()
                        
                        # 处理不同格式的输出
                        if "✖" in rest or "❌" in rest or "没有找到" in rest or "脚本运行失败" in rest:
                            # 无结果或错误的情况
                            results.append((script, rest, ""))
                        else:
                            # 尝试分离标题和链接
                            parts = rest.rsplit(" ", 1)
                            if len(parts) == 2 and (parts[1].startswith("http") or parts[1].startswith("www")):
                                title, link = parts
                                results.append((script, title.strip(), link.strip()))
                            else:
                                results.append((script, rest.strip(), ""))
                    except Exception as e:
                        st.warning(f"解析行出错: {line}")
                        continue
                
                if results:
                    df = pd.DataFrame(results, columns=["脚本", "标题", "链接"])
                    
                    # 显示结果数量
                    total_scripts = len(df['脚本'].unique())
                    total_results = len(df[df['链接'] != ''])
                    st.success(f"✅ 查询成功，共处理 {total_scripts} 个脚本，找到 {total_results} 条有效记录")
                    
                    # 显示统计信息
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("总脚本数", total_scripts)
                    with col2:
                        st.metric("有结果的脚本", len(df[(df['链接'] != '') & (df['标题'] != '')]['脚本'].unique()))
                    with col3:
                        st.metric("总记录数", len(df))
                    
                    # 显示表格
                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "链接": st.column_config.LinkColumn("链接")
                        }
                    )
                    
                    # 提供下载csv
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 下载 CSV",
                        data=csv_data,
                        file_name=f"results_{date_str}.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning("没有找到任何结果")
                
                # 显示运行日志
                with st.expander("📄 完整运行日志"):
                    st.code(result.stdout)
