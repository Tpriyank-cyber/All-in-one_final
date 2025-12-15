# -*- coding: utf-8 -*-
"""
Created on Mon Dec 15 12:17:20 2025
@author: tpriyank
"""

import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

# ===================== PAGE CONFIG =====================
favicon = "favicon.png"
st.set_page_config(
    page_title="Multi-Tech Data Processing Application",
    page_icon=favicon,
    layout="wide"
)

# ===================== CUSTOM CSS =====================
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.stApp {background-color: #ffffff; font-family: "Nokia Pure Headline Light";}
section[data-testid="stSidebar"] {background-color: #f5f0fa;}
h1, h2, h3 {color: #001135; font-family: "Nokia Pure Headline";}
label, .stMarkdown, .stText {color: #001135; font-size:16px;}
.stButton > button {background-color: #a235b6; color:white; font-weight:bold; border-radius:6px;}
.stButton > button:hover {background-color:#842b94;}
[data-testid="stDataFrame"] {border:1px solid #a235b6; border-radius:6px;}
</style>
""", unsafe_allow_html=True)

# ===================== SIDEBAR =====================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#660a93;'>Data Processing Tool</h2>", unsafe_allow_html=True)
    selected = option_menu(
        menu_title="Airtel Zambia",
        options=["About", "Tool", "Contact Us"],
        icons=["person", "slack", "telephone"],
        menu_icon=None,
        styles={
            "menu-title": {"color": "#660a93", "font-weight": "bold", "text-align": "center"},
            "nav-link": {"color": "#61206d", "font-size": "16px", "font-weight": "bold"},
            "nav-link-selected": {"background-color": "#a235b6", "color": "white"}
        }
    )


KPI_DICT = {
    "3G": [
        'CS RRC Setup Success Rate', 'PS RRC Setup Success Rate',
        'CS and Video RAB Setup Success Rate', 'PS and HS RAB Setup Success Rate',
        'CS_drop_rate', 'HS Drop Call Rate', 'Act HS-DSCH  end usr thp',
        'Cell Availability, excluding blocked by user state (BLU)',
        'Total CS traffic - Erl', 'Max simult HSDPA users',
        'Total_Data_Payload_DL_UL', 'Soft HO Success rate, RT',
        'Average RTWP'
    ],
    "LTE": [
        'Cell Avail excl BLU', 'Total E-UTRAN RRC conn stp SR',
        'E-UTRAN E-RAB stp SR', 'E-RAB DR RAN',
        'E-UTRAN Avg PRB usage per TTI DL', 'Average CQI',
        'Avg RRC conn UE', 'Avg IP thp DL QCI9',
        'Total LTE data volume, DL + UL',
        'Avg UE distance', 'Intra eNB HO SR',
        'E-UTRAN Intra-Freq HO SR', 'E-UTRAN Inter-Freq HO SR'
    ],
    "5G": [
        'MAC SDU data vol trans DL DTCH', 'MAC SDU data vol rcvd UL DTCH',
        'Cell avail exclud BLU', 'Max nr NSA user',
        'NSA Avg nr user', 'Sched MAC PDU user thp PDSCH prb util',
        'Sched MAC PDU user thp PUSCH prb util',
        'NSA call access', 'SgNB add prep SR',
        'SgNB t abn rel R excl X2 rst',
        'Inafreq inaDU PSC chg tot SR',
        'IntergNB HO SR NSA', 'Avg wb CQI 256QAM',
        'PRB util PDSCH', 'PRB util PUSCH',
        'NSA Adm rej R lack PUCCH rsrc'
    ],
    "2G": [
        'Total Traffic Erlangs', 'Call Setup Success Rate',
        'SDCCH BLOCKING RATE (%)', 'SDCCH Drop Rate(%)',
        'TCH Blocking', 'HOSR_mapa',
        'TCH availability ratio', 'Cell avail accuracy 1s cellL',
        'TASR_contractual', 'DL cumulative quality ratio in class 5',
        'Average SDCCH traffic', 'TCH Drop Rate',
        'TOT_VOL_DATA_DOWNLOADED'
    ]
}

COLUMN_DICT = {
    "3G": "WCEL name",
    "LTE": "LNCEL name",
    "5G": "NRCEL name",
    "2G": "Segment Name"
}

SITE_COL_DICT = {
    "2G": None,
    "3G": "WBTS name",
    "LTE": "MRBTS name",
    "5G": "MRBTS name"
}


def safe_kpis(df, tech):
    available = [k for k in KPI_DICT[tech] if k in df.columns]
    df[available] = df[available].apply(pd.to_numeric, errors='coerce')
    return available


def process_kpi(df, tech, available_kpis, cell_col):
    sheet_type = st.selectbox(
        f"Select Sheet Type for {tech}",
        ["BBH (Cell Day)", "Continue (Hour / Day)"],
        key=f"{tech}_sheet"
    )

    site_col = SITE_COL_DICT.get(tech)

    index_cols = []
    if site_col and site_col in df.columns:
        index_cols.append(site_col)

    if cell_col not in df.columns:
        st.error(f"❌ {tech}: Cell column '{cell_col}' not found")
        return

    index_cols.append(cell_col)

    if 'Date' not in df.columns:
        st.error("❌ Date column missing")
        return

    if sheet_type == "BBH (Cell Day)":
        pivot = pd.pivot_table(
            df,
            index=index_cols,
            columns='Date',
            values=available_kpis,
            aggfunc='sum'
        )

        pivot = pivot.stack(level=0).reset_index()
        pivot.rename(columns={pivot.columns[len(index_cols)]: 'KPI NAME'}, inplace=True)

        st.success(f"✅ {tech} Day Cell Level KPI Generated")
        st.dataframe(pivot, use_container_width=True)

    else:
        unique_dates = df['Date'].nunique()

        if unique_dates == 1:
            pivot = pd.pivot_table(
                df,
                index=index_cols,
                columns=['Date', 'Hour'],
                values=available_kpis,
                aggfunc='sum'
            )

            pivot = pivot.stack(level=0).reset_index()
            pivot.rename(columns={pivot.columns[len(index_cols)]: 'KPI NAME'}, inplace=True)

            st.success(f"✅ {tech} Hour Cell Level KPI Generated")
            st.dataframe(pivot, use_container_width=True)

        else:
            hour = st.number_input(f"Select Hour for {tech}", 0, 23, key=f"{tech}_hour")
            df_h = df[df["Hour"] == hour]

            if df_h.empty:
                st.warning("⚠ No data for selected hour")
                return

            pivot = pd.pivot_table(
                df_h,
                index=index_cols,
                columns='Date',
                values=available_kpis,
                aggfunc='sum'
            )

            pivot = pivot.stack(level=0).reset_index()
            pivot.rename(columns={pivot.columns[len(index_cols)]: 'KPI NAME'}, inplace=True)

            st.success(f"✅ {tech} Hour {hour} KPI Generated")
            st.dataframe(pivot, use_container_width=True)


# ===================== ABOUT =====================
if selected == "About":
    st.markdown("## ℹ Tool Introduction")
    st.write(
        "This Multi-Tech Data Processing tool automates **Day & Hour level KPI aggregation** "
        "for **Cell and PLMN views**, enabling faster and accurate OSS-based performance analysis."
    )
    st.markdown("## 🚀 Key Capabilities")
    st.markdown("""
    - Day & Hour KPI aggregation  
    - Cell & PLMN level analysis  
    """)



if selected == "Tool":
    st.markdown("## 📊 Multi-Tech Data Processing Application")
    st.write("**Developed by Priyank Tomar**")

    for tech in ["3G", "LTE", "5G", "2G"]:
        st.markdown(f"### 📂 Upload {tech} KPI File")
        file = st.file_uploader(f"{tech} File", type=["xlsx", "xls"], key=tech)

        if file:
            df = pd.read_excel(file)
            df.columns = df.columns.str.strip()
            df['Period start time'] = pd.to_datetime(df['Period start time'], errors='coerce')
            df["Date"] = df["Period start time"].dt.date
            df["Hour"] = df["Period start time"].dt.hour

            available = safe_kpis(df, tech)
            process_kpi(df, tech, available, COLUMN_DICT[tech])


if selected == "Contact Us":
    st.markdown("## 📞 Contact Us")
    st.write(
        "**Developer:** Priyank Tomar  \n"
        "**Domain:** 2G / 3G / LTE / 5G / OSS / KPI Automation   \n"
        "**Email:** tomar.priyank@nokia.com"
    )


