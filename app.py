import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import math

# 設定頁面標題
st.set_page_config(page_title="高爾頓板模擬器", layout="centered")

st.title("高爾頓板 (Galton Board) 模擬")

# 插入描述與原理解釋
st.markdown("""
> **高爾頓板（Galton board）**是由一塊帶有交錯排列釘子的直立板塊所構成。當裝置保持水平時，從頂部丟下珠子，珠子在撞擊釘子時會隨機向左或向右彈跳。最終它們會收集在底部的凹槽中，累積在凹槽裡的珠子圓柱高度會近似於**鐘形曲線（常態分佈）**。
> 
> 將**帕斯卡三角形（Pascal's triangle）**疊加在釘子上，可以顯示出到達每個凹槽的不同路徑數量。
""")

st.divider()

# 側邊欄控制參數
st.sidebar.header("控制面板")
levels = st.sidebar.slider("釘子層數 (Rows of pegs)", min_value=3, max_value=50, value=15, step=1)
beads = st.sidebar.slider("珠子總數 (Number of beads)", min_value=100, max_value=50000, value=10000, step=500)

# --- 模擬核心邏輯 ---
# 每顆珠子在每一層都有 50% 的機率向右跳。向右跳的總次數即為最後落入的凹槽索引。
# 這是一個典型的二項式分佈 (Binomial Distribution)，可透過 numpy 快速模擬。
final_positions = np.random.binomial(levels, 0.5, beads)

# --- 繪圖 ---
fig, ax = plt.subplots(figsize=(10, 6))

# 繪製直方圖 (代表底部的凹槽與累積的珠子)
bins = np.arange(-0.5, levels + 1.5, 1)
counts, edges, patches = ax.hist(
    final_positions, 
    bins=bins, 
    rwidth=0.8, 
    color='#4C92C3', 
    edgecolor='black', 
    alpha=0.8, 
    label='模擬珠子分佈'
)

# 繪製理論上的常態分佈曲線 (鐘形曲線)
mu = levels / 2.0                 # 平均值
sigma = math.sqrt(levels) / 2.0   # 標準差
x = np.linspace(0, levels, 200)
# 將 PDF 乘上珠子總數以匹配直方圖的刻度
y = norm.pdf(x, mu, sigma) * beads 
ax.plot(x, y, 'r-', lw=3, label='理論鐘形曲線 (Bell Curve)')

ax.set_title(f"丟下 {beads} 顆珠子後的結果", fontsize=16)
ax.set_xlabel("凹槽編號 (向右彈跳的次數)", fontsize=12)
ax.set_ylabel("珠子數量", fontsize=12)
ax.set_xticks(range(0, levels + 1))
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.7)

# 在 Streamlit 顯示圖表
st.pyplot(fig)

# --- 帕斯卡三角形路徑數 ---
st.subheader("帕斯卡三角形與路徑數")
st.markdown(f"當珠子穿過 **{levels}** 層釘子時，到達第 $k$ 個凹槽的路徑總數剛好等於帕斯卡三角形第 {levels} 層的組合數 $C({levels}, k)$：")

# 計算路徑組合數
paths = [math.comb(levels, k) for k in range(levels + 1)]

# 將數據格式化為容易閱讀的長字串或表格
paths_str = " | ".join([f"**凹槽 {k}**: {p} 條" for k, p in enumerate(paths)])
st.info(paths_str)

total_paths = sum(paths)
st.write(f"**總路徑數**：$2^{{{levels}}} = {total_paths:,}$ 條可能路徑。")
