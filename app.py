import streamlit as st
import pandas as pd
import os
import subprocess
import sys
from datetime import datetime

import os
if not os.path.exists("/home/appuser/.cache/ms-playwright"):
    os.system("playwright install chromium")

st.set_page_config(page_title="Betting Smart Dashboard", layout="wide")

st.markdown("""
    <style>
    section[data-testid="stSidebar"] { background-color: #1a1c1e; }
    .stMetric { border: 1px solid #333; padding: 15px; border-radius: 10px; background-color: #262730; }
    .combo-card { 
        background-color: #262730; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #00ffcc;
        margin-bottom: 15px;
    }
    .investment-box {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #444;
        margin-bottom: 25px;
    }
    .status-msg {
        background-color: #2d303d;
        padding: 10px;
        border-radius: 8px;
        font-size: 0.85em;
        color: #a0a0a0;
        text-align: center;
        border: 1px solid #3e4150;
    }
    .no-combo {
        padding: 20px;
        border: 1px dashed #555;
        border-radius: 10px;
        text-align: center;
        color: #888;
    }
    </style>
    """, unsafe_allow_html=True)

EXCEL_FILE = "matches_daily.xlsx"
HISTORY_FILE = "picks_history.csv"

with st.sidebar:
    st.title("🎮 Action Center")
    if st.button("🚀 RUN WISE SCAN", type="primary", use_container_width=True):
        with st.spinner("Analyzing Leagues & Probabilities..."):
            subprocess.run([sys.executable, "scraper.py"])
            st.rerun()
    
    st.divider()
    selected_leagues = []
    if os.path.exists(EXCEL_FILE):
        df_all = pd.read_excel(EXCEL_FILE)
        available_leagues = sorted([l for l in df_all['league'].unique() if pd.notna(l) and l != ""])
        st.write("📂 **League Filters**")
        selected_leagues = st.multiselect("Select Competitions:", available_leagues, default=[])
        mtime = datetime.fromtimestamp(os.path.getmtime(EXCEL_FILE)).strftime('%H:%M:%S')
        st.write(f"🕒 **Last Update:** {mtime}")

st.title("⚽ Betting Smart Dashboard")
tab1, tab2 = st.tabs(["🎯 Live Picks", "📚 Saved History"])

with tab1:
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        if selected_leagues:
            df = df[df['league'].isin(selected_leagues)]
            
        rec_df = df[df['status'].isin(['ELITE', 'VALUE'])].copy()

        # --- 1. NUMERICAL STATS ---
        elite_df = rec_df[rec_df['status'] == 'ELITE'].sort_values(by='risk_score')
        value_df = rec_df[rec_df['status'] == 'VALUE'].sort_values(by='risk_score')
        
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1: st.metric("💎 Elite Picks", len(elite_df))
        with m_col2: st.metric("📊 Value Picks", len(value_df))
        with m_col3: 
            edge = f"{df['ev_percent'].mean():.1f}%" if 'ev_percent' in df.columns else "N/A"
            st.metric("🔎 Avg Market Edge", edge)

        st.divider()

        # --- 2. UPDATED INVESTMENT CALCULATOR ---
        if not rec_df.empty:
            st.markdown("### 💰 Daily Capital Allocation")
            st.markdown('<div class="investment-box">', unsafe_allow_html=True)
            
            daily_capital = st.number_input("Enter Today's Working Capital ($):", min_value=0, value=100, step=10)
            inv_col1, inv_col2 = st.columns(2)
            
            with inv_col1:
                st.markdown("**🛡️ Anchor Strategy (60%)**")
                if len(elite_df) >= 2:
                    stake = daily_capital * 0.60
                    # Kelly Criterion Logic: Stake based on Edge
                    kelly_f = 0.2 # conservative multiplier
                    edge_val = elite_df.iloc[0].get('ev_percent', 0) / 100
                    k_stake = max(0, daily_capital * edge_val * kelly_f) if edge_val > 0 else stake
                    
                    odds = round(elite_df.head(2)['h_odds'].prod(), 2)
                    st.success(f"Stake: **${stake:,.2f}**")
                    st.caption(f"💡 Kelly Suggestion for top pick: ${k_stake:.2f}")
                    st.write(f"Target Odds: {odds} | Return: **${round(stake * odds, 2)}**")
                else:
                    st.markdown(f'<div class="status-msg">⚠️ Need more Elites ({len(elite_df)}/2 found)</div>', unsafe_allow_html=True)

            with inv_col2:
                st.markdown("**⚖️ Hybrid Strategy (40%)**")
                safe_values = value_df[(value_df['risk_score'] >= 6.0) & (value_df['risk_score'] <= 7.5)]
                if len(elite_df) >= 1 and len(safe_values) >= 1:
                    stake = daily_capital * 0.40
                    odds = round(elite_df.iloc[0]['h_odds'] * safe_values.iloc[0]['h_odds'], 2)
                    st.warning(f"Stake: **${stake:,.2f}**")
                    st.write(f"Target Odds: {odds} | Return: **${round(stake * odds, 2)}**")
                else:
                    st.markdown(f'<div class="status-msg">⏳ Elite: {len(elite_df)}/1 | Safe Value: {len(safe_values)}/0</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Run a scan to activate the Investment Calculator.")

        # --- 3. SMART DECISION SUGGESTIONS ---
        st.markdown("### 🛡️ Smart Decision Suggestions")
        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            if len(elite_df) >= 2:
                d_pair = elite_df.head(2)
                st.markdown(f"""<div class="combo-card">
                <b>💎 Ultra-Safe Elite Double</b><br>
                {d_pair.iloc[0]['home']} + {d_pair.iloc[1]['home']}<br>
                Avg Risk: <b>{round(d_pair['risk_score'].mean(),1)}/10</b>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div class="no-combo">📝 <i>Needs at least 2 Elite matches.</i></div>', unsafe_allow_html=True)

        with col_s2:
            safe_values = value_df[(value_df['risk_score'] >= 6.0) & (value_df['risk_score'] <= 7.5)]
            if len(elite_df) >= 1 and len(safe_values) >= 2:
                st.markdown(f"""<div class="combo-card" style="border-left-color: #ffaa00;">
                <b>⚖️ Hybrid Stability Triple</b><br>
                Elite: {elite_df.iloc[0]['home']}<br>
                Value: {safe_values.iloc[0]['home']} + {safe_values.iloc[1]['home']}
                </div>""", unsafe_allow_html=True)
            elif len(elite_df) >= 1 and len(safe_values) >= 1:
                st.markdown(f"""<div class="combo-card" style="border-left-color: #ffaa00;">
                <b>⚖️ Hybrid Double</b><br>
                {elite_df.iloc[0]['home']} + {safe_values.iloc[0]['home']}<br>
                Risk Category: <b>Balanced</b>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div class="no-combo">📭 <i>Needs 1 Elite + Value (6.0-7.5 risk).</i></div>', unsafe_allow_html=True)
        
        st.write("") 

        # --- 4. ORIGINAL TABLE UI ---
        st.markdown("### 🌟 Recommended Assignments")
        if not rec_df.empty:
            st.dataframe(
                rec_df[['league', 'home', 'away', 'h_odds', 'prob_1x', 'risk_score', 'ev_percent', 'time', 'status']], 
                column_config={
                    "prob_1x": st.column_config.ProgressColumn("Safety Buffer (1X)", format="%.1f%%", min_value=0, max_value=100),
                    "risk_score": st.column_config.NumberColumn("Risk", format="%.1f/10"),
                    "ev_percent": st.column_config.NumberColumn("EV Edge %", format="%.1f%%"),
                    "league": "Competition"
                },
                use_container_width=True, hide_index=True
            )
        else:
            st.info("No high-probability picks found.")

        with st.expander("🔍 View All Scanned Games"):
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("No data. Run a scan to fetch matches.")

with tab2:
    st.markdown("### 📈 Historical Log")
    if os.path.exists(HISTORY_FILE):
        h_df = pd.read_csv(HISTORY_FILE).iloc[::-1]
        st.dataframe(h_df, use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("📊 Performance Analytics by League")
        if 'ev_percent' in h_df.columns:
            l_stats = h_df.groupby('league').agg({'ev_percent': 'mean', 'home': 'count'}).rename(columns={'home': 'Count', 'ev_percent': 'Avg Edge %'})
            st.table(l_stats.sort_values(by='Avg Edge %', ascending=False))
        
        st.download_button("📥 Export CSV", data=h_df.to_csv(index=False), file_name="history.csv", mime="text/csv")