import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Image, Spacer, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm

st.set_page_config(
    page_title="Custom BI Tool",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
    <style>
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1E2130;
        border-right: 1px solid #F0A500;
    }

    /* Sidebar filter tags — gold instead of red */
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background-color: #F0A500 !important;
        color: #0F1117 !important;
        font-weight: 600 !important;
    }

    /* Sidebar filter label background remove */
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stSlider label {
        background-color: transparent !important;
        color: #FAFAFA !important;
        font-weight: 600 !important;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: #1E2130;
        border: 1px solid #F0A500;
        border-radius: 10px;
        padding: 16px;
    }

    /* Metric label */
    [data-testid="stMetricLabel"] {
        color: #F0A500 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Buttons */
    [data-testid="stButton"] button {
        background-color: #F0A500;
        color: #0F1117;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 8px 20px;
    }
    [data-testid="stButton"] button:hover {
        background-color: #D4920A;
        color: #0F1117;
    }

    /* Download button */
    [data-testid="stDownloadButton"] button {
        background-color: #262B3D;
        color: #F0A500;
        font-weight: 600;
        border: 1px solid #F0A500;
        border-radius: 8px;
    }

    /* Divider */
    hr {
        border-color: #F0A500 !important;
        opacity: 0.3;
    }

    /* Title */
    h1 {
        color: #F0A500 !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    /* Subheaders */
    h2, h3 {
        color: #FAFAFA !important;
        font-weight: 600 !important;
    }

    /* Success message */
    [data-testid="stAlert"] {
        background-color: #1E2130;
        border-left: 4px solid #F0A500;
        color: #FAFAFA;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #262B3D;
        border-radius: 8px;
    }



    /* Selectbox & multiselect */
    [data-testid="stSelectbox"] > div,
    [data-testid="stMultiSelect"] > div {
        border-color: #F0A500 !important;
    }

   
    /* Slider */
    [data-testid="stSlider"] > div > div > div {
        background-color: #F0A500 !important;
    }
            
    /* Search label — bigger */
    [data-testid="stTextInput"] label p {
        font-size: 18px !important;
        font-weight: 700 !important;
        color: #F0A500 !important;
    }
            
    </style>
""", unsafe_allow_html=True)
st.title("Custom BI-style Dashboard")

uploaded_file = st.file_uploader("Upload excel file", type=["xlsx", "xls"])

if uploaded_file:
    xl = pd.ExcelFile(uploaded_file)
    sheet_names = xl.sheet_names

    if len(sheet_names) > 1:
        selected_sheet = st.selectbox("📄 Select preferred sheet", sheet_names)
    else:
        selected_sheet = sheet_names[0]

    df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
    st.success(f"✅ File loaded: {df.shape[0]} rows, {df.shape[1]} columns")

    num_cols = df.select_dtypes(include='number').columns.tolist()
    cat_cols = [col for col in df.select_dtypes(exclude='number').columns
                if not pd.api.types.is_datetime64_any_dtype(df[col])]

    # ── FILTERS ──────────────────────────────────────────
    # ── FILTERS ──────────────────────────────────────────
    st.sidebar.header(" Filters")
    filtered_df = df.copy()

    # Date range filter
    date_cols = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
    if date_cols:
        date_col = date_cols[0]
        min_date = df[date_col].min().date()
        max_date = df[date_col].max().date()
        selected_dates = st.sidebar.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        if len(selected_dates) == 2:
            filtered_df = filtered_df[
                (filtered_df[date_col].dt.date >= selected_dates[0]) &
                (filtered_df[date_col].dt.date <= selected_dates[1])
            ]

    for col in cat_cols[:3]:
        options = df[col].dropna().unique().tolist()
        selected = st.sidebar.multiselect(f"{col}", options, default=options)
        filtered_df = filtered_df[filtered_df[col].isin(selected)]

    for col in num_cols[:2]:
        col_min = float(df[col].min())
        col_max = float(df[col].max())
        selected_range = st.sidebar.slider(
            f"{col} range",
            min_value=col_min,
            max_value=col_max,
            value=(col_min, col_max)
        )
        filtered_df = filtered_df[
            (filtered_df[col] >= selected_range[0]) &
            (filtered_df[col] <= selected_range[1])
        ]

    st.sidebar.markdown(f"**Rows after filter: {len(filtered_df)}**")
    # ─────────────────────────────────────────────────────

    # --- KPI Alerts ---
    st.sidebar.divider()
    st.sidebar.subheader("🎯 KPI Target")
    kpi_col = st.sidebar.selectbox("Monitor column", num_cols, key="kpi_col")
    kpi_condition = st.sidebar.selectbox("Condition", ["Less than", "Greater than"], key="kpi_cond")
    kpi_target = st.sidebar.number_input("Target value", min_value=0.0, value=10000.0, step=100.0, key="kpi_target")

    # --- Metrics ---
    if num_cols:
        kpi_actual = filtered_df[kpi_col].sum()
        kpi_met = (kpi_condition == "Greater than" and kpi_actual >= kpi_target) or \
                  (kpi_condition == "Less than" and kpi_actual < kpi_target)

        if kpi_met:
            st.success(f"✅ KPI Met — {kpi_col} is {kpi_actual:,.0f} | Target: {kpi_condition} {kpi_target:,.0f}")
        else:
            st.error(f"🔴 KPI Alert — {kpi_col} is {kpi_actual:,.0f} | Target: {kpi_condition} {kpi_target:,.0f}")

        cols = st.columns(min(4, len(num_cols)))
        for i, col in enumerate(num_cols[:4]):
            actual = filtered_df[col].sum()
            if col == kpi_col:
                delta_color = "normal" if kpi_met else "inverse"
                cols[i].metric(
                    col,
                    f"{actual:,.0f}",
                    f"Target: {kpi_target:,.0f}",
                    delta_color=delta_color
                )
            else:
                cols[i].metric(col, f"{actual:,.0f}", f"Avg: {filtered_df[col].mean():,.1f}")

    st.divider()

    # --- Charts ---
    col1, col2 = st.columns(2)

    with col1:
        x_axis = st.selectbox("X-axis (category)", cat_cols or df.columns.tolist())
        y_axis = st.selectbox("Y-axis (value)", num_cols or df.columns.tolist())
        chart_type = st.selectbox("Chart type", ["Bar", "Line", "Pie", "Scatter", "Area", "Donut", "Box Plot", "Funnel", "Treemap"])

        grouped = filtered_df.groupby(x_axis)[y_axis].sum().reset_index().sort_values(y_axis, ascending=False).head(15)

        if chart_type == "Bar":
            fig = px.bar(grouped, x=x_axis, y=y_axis, color=y_axis, color_continuous_scale="Blues")
        elif chart_type == "Line":
            fig = px.line(grouped, x=x_axis, y=y_axis, markers=True)
            import numpy as np
            if len(grouped) >= 2:
                x_numeric = np.arange(len(grouped))
                y_values = grouped[y_axis].values
                z = np.polyfit(x_numeric, y_values, 1)
                p = np.poly1d(z)
                trend_y = p(x_numeric)
                fig.add_scatter(
                    x=grouped[x_axis],
                    y=trend_y,
                    mode="lines",
                    name="Trend",
                    line=dict(color="#F0A500", dash="dot", width=2)
                )
        elif chart_type == "Pie":
            fig = px.pie(grouped, names=x_axis, values=y_axis)
        elif chart_type == "Scatter":
            fig = px.scatter(filtered_df, x=x_axis, y=y_axis)
        elif chart_type == "Area":
            fig = px.area(grouped, x=x_axis, y=y_axis)
        elif chart_type == "Donut":
            fig = px.pie(grouped, names=x_axis, values=y_axis, hole=0.4)
        elif chart_type == "Box Plot":
            fig = px.box(filtered_df, x=x_axis, y=y_axis)
        elif chart_type == "Funnel":
            fig = px.funnel(grouped, x=y_axis, y=x_axis)
        elif chart_type == "Treemap":
            fig = px.treemap(grouped, path=[x_axis], values=y_axis)

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        if num_cols:
            hist_col = st.selectbox("Distribution column", num_cols)
            fig2 = px.histogram(filtered_df, x=hist_col, nbins=20, color_discrete_sequence=["#1D9E75"])
            st.plotly_chart(fig2, use_container_width=True)

  # --- Pivot Table ---
    st.subheader("Pivot Table")
    pivot_col1, pivot_col2, pivot_col3 = st.columns(3)
    with pivot_col1:
        pivot_rows = st.selectbox("Rows", cat_cols, key="pivot_rows")
    with pivot_col2:
        pivot_cols_sel = st.selectbox("Columns", cat_cols, key="pivot_cols")
    with pivot_col3:
        pivot_vals = st.selectbox("Values", num_cols, key="pivot_vals")
    if pivot_rows == pivot_cols_sel:
        st.warning("Rows and Columns cannot be the same. Please select different columns.")
    else:
        pt = filtered_df.pivot_table(
            index=pivot_rows,
            columns=pivot_cols_sel,
            values=pivot_vals,
            aggfunc="sum",
            fill_value=0,
            margins=True,
            margins_name="Total"
        )
        pt = pt.round(0).astype(int)
        st.dataframe(pt, use_container_width=True)
        csv_pivot = pt.to_csv().encode("utf-8")
        st.download_button(
            "⬇️ Download Pivot Table",
            csv_pivot,
            "pivot_table.csv",
            "text/csv",
            key="pivot_download"
        )

    st.divider()        

    # --- Data Table ---
    st.subheader("Data Preview")
    search_query = st.text_input("**Search in Table**", placeholder="type to search...")
    if search_query:
        mask = filtered_df.astype(str).apply(lambda row: row.str.contains(search_query, case=False, na=False)).any(axis=1)
        display_df = filtered_df[mask]
    else:
        display_df = filtered_df
    st.caption(f"Showing {len(display_df)} of {len(filtered_df)} rows")
    display_df_formatted = display_df.copy()
    for col in display_df_formatted.columns:
        if pd.api.types.is_datetime64_any_dtype(display_df_formatted[col]):
            display_df_formatted[col] = display_df_formatted[col].dt.strftime("%d %b %Y")
    st.dataframe(display_df_formatted.head(100), use_container_width=True)

    # --- PDF EXPORT ──────────────────────────────────────
    st.divider()
    st.subheader("📥 Export Report")

    company_name = "Your Company Name"

    if st.button("Generate PDF Report"):
        with st.spinner("PDF is being created..."):

            img1 = io.BytesIO(fig.to_image(format="png", width=800, height=450, scale=2))
            img2 = io.BytesIO(fig2.to_image(format="png", width=800, height=450, scale=2))

            pdf_buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=landscape(A4),
                leftMargin=1.5*cm,
                rightMargin=1.5*cm,
                topMargin=1.5*cm,
                bottomMargin=2*cm
            )

            styles = getSampleStyleSheet()
            story = []

            BLUE_DARK  = colors.HexColor("#0C447C")
            BLUE_MID   = colors.HexColor("#185FA5")
            BLUE_LIGHT = colors.HexColor("#E6F1FB")
            GRAY_BG    = colors.HexColor("#F1EFE8")
            GRAY_LINE  = colors.HexColor("#B4B2A9")
            WHITE      = colors.white

            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
            from datetime import datetime

            header_data = [[
                Paragraph(f'<font size="18" color="white"><b>{company_name}</b></font>', styles['Normal']),
                Paragraph(f'<font size="11" color="white">Dashboard Report</font><br/><font size="9" color="white">Generated: {datetime.now().strftime("%d %B %Y, %I:%M %p")}</font>', styles['Normal'])
            ]]
            header_tbl = Table(header_data, colWidths=[14*cm, 13*cm])
            header_tbl.setStyle(TableStyle([
                ('BACKGROUND',    (0,0), (-1,-1), BLUE_DARK),
                ('TOPPADDING',    (0,0), (-1,-1), 14),
                ('BOTTOMPADDING', (0,0), (-1,-1), 14),
                ('LEFTPADDING',   (0,0), (-1,-1), 16),
                ('RIGHTPADDING',  (0,0), (-1,-1), 16),
                ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN',         (1,0), (1,0),   'RIGHT'),
            ]))
            story.append(header_tbl)
            story.append(Spacer(1, 0.5*cm))

            summary_data = [[
                Paragraph(f'<font size="10" color="#0C447C">Total Rows (filtered)</font><br/><font size="16"><b>{len(filtered_df):,}</b></font>', styles['Normal']),
                Paragraph(f'<font size="10" color="#0C447C">Total Columns</font><br/><font size="16"><b>{len(df.columns)}</b></font>', styles['Normal']),
                Paragraph(f'<font size="10" color="#0C447C">File Name</font><br/><font size="11"><b>{uploaded_file.name}</b></font>', styles['Normal']),
                Paragraph(f'<font size="10" color="#0C447C">Chart Type</font><br/><font size="11"><b>{chart_type}</b></font>', styles['Normal']),
            ]]
            summary_tbl = Table(summary_data, colWidths=[6.75*cm]*4)
            summary_tbl.setStyle(TableStyle([
                ('BACKGROUND',    (0,0), (-1,-1), BLUE_LIGHT),
                ('TOPPADDING',    (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                ('LEFTPADDING',   (0,0), (-1,-1), 14),
                ('GRID',          (0,0), (-1,-1), 0.5, GRAY_LINE),
            ]))
            story.append(summary_tbl)
            story.append(Spacer(1, 0.4*cm))

            from reportlab.platypus import HRFlowable
            story.append(Paragraph('<font size="12" color="#0C447C"><b>Key Metrics</b></font>', styles['Normal']))
            story.append(Spacer(1, 0.15*cm))
            story.append(HRFlowable(width="100%", thickness=1.5, color=BLUE_MID))
            story.append(Spacer(1, 0.15*cm))

            metric_data = [[
                Paragraph('<b>Column</b>', styles['Normal']),
                Paragraph('<b>Total</b>', styles['Normal']),
                Paragraph('<b>Average</b>', styles['Normal']),
                Paragraph('<b>Min</b>', styles['Normal']),
                Paragraph('<b>Max</b>', styles['Normal']),
            ]]
            for col in num_cols[:4]:
                metric_data.append([
                    col,
                    f"{filtered_df[col].sum():,.0f}",
                    f"{filtered_df[col].mean():,.1f}",
                    f"{filtered_df[col].min():,.1f}",
                    f"{filtered_df[col].max():,.1f}",
                ])

            metric_tbl = Table(metric_data, colWidths=[7*cm, 4*cm, 4*cm, 4*cm, 4*cm])
            metric_tbl.setStyle(TableStyle([
                ('BACKGROUND',    (0,0), (-1,0),  BLUE_MID),
                ('TEXTCOLOR',     (0,0), (-1,0),  WHITE),
                ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
                ('FONTSIZE',      (0,0), (-1,-1), 10),
                ('ALIGN',         (1,0), (-1,-1), 'CENTER'),
                ('ROWBACKGROUNDS',(0,1), (-1,-1), [BLUE_LIGHT, WHITE]),
                ('GRID',          (0,0), (-1,-1), 0.5, GRAY_LINE),
                ('TOPPADDING',    (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING',   (0,0), (-1,-1), 10),
            ]))
            story.append(metric_tbl)
            story.append(Spacer(1, 0.4*cm))

            story.append(Paragraph('<font size="12" color="#0C447C"><b>Charts</b></font>', styles['Normal']))
            story.append(Spacer(1, 0.15*cm))
            story.append(HRFlowable(width="100%", thickness=1.5, color=BLUE_MID))
            story.append(Spacer(1, 0.2*cm))

            charts_data = [[Image(img1, width=13*cm, height=7.5*cm), Image(img2, width=13*cm, height=7.5*cm)]]
            charts_tbl = Table(charts_data, colWidths=[13.5*cm, 13.5*cm])
            charts_tbl.setStyle(TableStyle([
                ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
                ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING',  (0,0), (-1,-1), 4),
                ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(charts_tbl)

            story.append(Spacer(1, 0.4*cm))
            story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY_LINE))
            story.append(Spacer(1, 0.15*cm))
            story.append(Paragraph(
                f'<font size="8" color="#888780">Confidential — {company_name} — Generated on {datetime.now().strftime("%d %B %Y")}</font>',
                ParagraphStyle('footer', alignment=TA_CENTER)
            ))

            doc.build(story)
            pdf_buffer.seek(0)

        st.download_button(
            label="⬇️ Download PDF",
            data=pdf_buffer,
            file_name=f"dashboard_report_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )

    # --- Download CSV ---
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Filtered CSV", csv, "filtered_data.csv", "text/csv")