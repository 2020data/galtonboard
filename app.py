import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# 設定頁面標題與佈局
st.set_page_config(page_title="動態高爾頓板模擬器", layout="centered")

st.title("高爾頓板 (Galton Board) 動態模擬 🎰")
st.markdown("觀察滾珠如何一顆顆穿梭在釘陣中，並自然地**散落、堆疊**在底部的實體分區凹槽中。")

st.divider()

# 側邊欄控制面板
st.sidebar.header("控制面板")
levels = st.sidebar.slider("釘子層數 (Rows of pegs)", min_value=5, max_value=15, value=10, step=1)

# 動畫與數量設定
animate = st.sidebar.checkbox("開啟掉落動畫 (較耗效能)", value=True)
if animate:
    beads = st.sidebar.slider("珠子總數", min_value=50, max_value=400, value=200, step=10)
    st.sidebar.caption("💡 提示：開啟動畫時，為確保順暢度，珠子數量上限設為 400。")
else:
    beads = st.sidebar.slider("珠子總數", min_value=100, max_value=2000, value=800, step=100)

# 材質顏色選擇
color_choice = st.sidebar.selectbox(
    "滾珠款式 (金屬質感)", 
    ["黃金 (Gold)", "白銀 (Silver)", "青銅 (Bronze)", "紅寶石 (Ruby)", "藍寶石 (Sapphire)", "翡翠 (Emerald)"]
)

# 顏色代碼映射表
color_map = {
    "黃金 (Gold)": "#FFD700",
    "白銀 (Silver)": "#E0E0E0",
    "青銅 (Bronze)": "#CD7F32",
    "紅寶石 (Ruby)": "#E52B50",
    "藍寶石 (Sapphire)": "#0F52BA",
    "翡翠 (Emerald)": "#50C878"
}
base_color = color_map[color_choice]

if st.button("🚀 開始投放滾珠"):
    # --- 1. 計算物理路徑與最終位置 ---
    paths = np.zeros((beads, levels + 1))
    for i in range(beads):
        # 每一層有一半機率向左(-0.5)或向右(+0.5)
        steps = np.random.choice([-0.5, 0.5], size=levels)
        paths[i, 1:] = np.cumsum(steps)
        
    final_bins = paths[:, -1]
    
    # 計算每個凹槽的堆疊高度 (計算這顆珠子是該凹槽的第幾顆)
    stack_idx = np.zeros(beads)
    current_counts = {}
    for i in range(beads):
        b = final_bins[i]
        if b not in current_counts:
            current_counts[b] = 0
        stack_idx[i] = current_counts[b]
        current_counts[b] += 1
        
    max_stack = max(current_counts.values()) if current_counts else 0

    # 為每顆珠子加入凹槽內的「左右散落偏移量 (Jitter)」
    np.random.seed(int(time.time()))
    jitter = np.random.uniform(-0.35, 0.35, beads)

    # --- 2. 準備 Matplotlib 畫布與座標系統 ---
    fig, ax = plt.subplots(figsize=(9, 7))
    fig.patch.set_facecolor('#1E1E1E') 
    ax.set_facecolor('#1E1E1E')
    
    # 計算畫面顯示邊界
    x_max = levels / 2.0 + 1
    y_max = 1
    
    # 設定底板位置與畫面最低點
    y_floor = -levels - (max_stack * 0.7) - 1.5
    y_min = y_floor - 0.5
    
    # 預先生成靜態的「釘子」座標
    peg_x, peg_y = [], []
    for r in range(levels):
        for i in range(r + 1):
            peg_x.append(i - r / 2.0)
            peg_y.append(-r)
            
    # 計算分區擋板的 X 座標
    wall_xs = np.arange(-levels/2 - 0.5, levels/2 + 1.5, 1)

    def draw_background():
        """繪製靜態背景：釘子、分區擋板與底板"""
        ax.set_xlim(-x_max, x_max)
        ax.set_ylim(y_min, y_max)
        ax.axis('off')
        # 畫釘陣 (白色半透明)
        ax.scatter(peg_x, peg_y, color='white', s=25, alpha=0.4, zorder=1)
        # 畫分區擋板
        for wx in wall_xs:
            ax.plot([wx, wx], [y_floor, -levels - 0.2], color='#777777', linewidth=2, alpha=0.6, zorder=1)
        # 畫底板
        ax.plot([wall_xs[0], wall_xs[-1]], [y_floor, y_floor], color='#777777', linewidth=4, alpha=0.8, zorder=1)

    plot_placeholder = st.empty()

    # 視覺參數：珠子大小與金屬反光偏移量
    bead_size = 100
    highlight_size = 20
    offset = 0.08 
    
    if animate:
        # --- 動態掉落運算 ---
        drop_rate = max(1, beads // 35) # 批次掉落數量
        fall_speed = 0.6                # 掉落速度
        max_steps = (beads // drop_rate) + levels + int((abs(y_floor) + max_stack) / fall_speed) + 5
        
        # 預先分配座標記憶體
        X = np.full((beads, max_steps), np.nan)
        Y = np.full((beads, max_steps), np.nan)
        
        progress_bar = st.progress(0)
        
        for i in range(beads):
            t_start = i // drop_rate
            
            # 第一階段：在釘子間彈跳
            for k in range(levels + 1):
                t_curr = t_start + k
                if t_curr < max_steps:
                    X[i, t_curr] = paths[i, k]
                    Y[i, t_curr] = -k
                    
            # 第二階段：落入底部凹槽並在分區內散落 (加入 Jitter)
            target_x = paths[i, levels] + jitter[i]
            # 由底板往上堆疊
            final_y = y_floor + 0.35 + (stack_idx[i] * 0.7)
            
            fall_dist = abs(-levels - final_y)
            fall_frames = int(fall_dist / fall_speed) + 1
            
            for f in range(1, fall_frames + 1):
                t_curr = t_start + levels + f
                if t_curr < max_steps:
                    # 在掉落過程中，X 座標漸漸往目標的散落位置靠攏
                    ratio = f / fall_frames
                    X[i, t_curr] = paths[i, levels] + (jitter[i] * ratio)
                    Y[i, t_curr] = max(-levels - f * fall_speed, final_y)
                    
            # 第三階段：乖乖停在堆疊位置
            t_rest = t_start + levels + fall_frames + 1
            if t_rest < max_steps:
                X[i, t_rest:] = target_x
                Y[i, t_rest:] = final_y

        # --- 播放動畫 ---
        for t in range(0, max_steps):
            ax.clear()
            draw_background()
            
            curr_x = X[:, t]
            curr_y = Y[:, t]
            valid = ~np.isnan(curr_x)
            
            if np.any(valid):
                vx = curr_x[valid]
                vy = curr_y[valid]
                
                # 繪製金屬珠子
                ax.scatter(vx, vy, color=base_color, s=bead_size, edgecolors='black', linewidth=0.8, zorder=2)
                ax.scatter(vx - offset, vy + offset, color='white', s=highlight_size, alpha=0.7, zorder=3)
                
            plot_placeholder.pyplot(fig)
            progress_bar.progress(min(1.0, (t + 1) / max_steps))
            
        progress_bar.empty()

    else:
        # --- 靜態直接顯示模式 ---
        draw_background()
        
        # 準備所有珠子的最終座標 (加入偏移與由下往上的堆疊)
        final_x = paths[:, -1] + jitter
        final_y = y_floor + 0.35 + (stack_idx * 0.7)
        
        # 繪製金屬質感珠子
        ax.scatter(final_x, final_y, color=base_color, s=bead_size, edgecolors='black', linewidth=0.8, zorder=2)
        ax.scatter(final_x - offset, final_y + offset, color='white', s=highlight_size, alpha=0.7, zorder=3)
        
        plot_placeholder.pyplot(fig)

    st.success("🎉 模擬完成！觀察珠子如何在實體凹槽中錯落有致地堆疊。")
