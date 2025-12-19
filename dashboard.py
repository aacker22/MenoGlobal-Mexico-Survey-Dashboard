import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path
import textwrap

px.defaults.template = "plotly_white"

# -------------------------------
# 1️⃣ Load data
# -------------------------------
BASE_DIR = Path(__file__).parent
df = pd.read_csv(BASE_DIR / "MenoGlobgal_Mexico_survey_ENG_Dec2025_clean.csv")

# -------------------------------
# 2️⃣ Define friendly names for survey questions
# -------------------------------
# Keys = raw column names in df, Values = display names in dashboard
column_display_names = {
    "12_clean": "Had you heard about perimenopause before taking this survey?",
    "19. Evaluate how comfortable you feel discussing menopause with: [Partner]": "Evaluate how comfortable you feel discussing menopause with: [Partner]",
    "19. Evaluate how comfortable you feel discussing menopause with: [Classmates]": "Evaluate how comfortable you feel discussing menopause with: [Classmates]",
    "19. Evaluate how comfortable you feel discussing menopause with: [Work colleagues]": "Evaluate how comfortable you feel discussing menopause with: [Work colleagues]",
    "19. Evaluate how comfortable you feel discussing menopause with: [Family members]": "Evaluate how comfortable you feel discussing menopause with: [Family members]",
    "19. Evaluate how comfortable you feel discussing menopause with: [Healthcare provider]": "Evaluate how comfortable you feel discussing menopause with: [Healthcare provider]",
    "19. Evaluate how comfortable you feel discussing menopause with: [Close friend]": "Evaluate how comfortable you feel discussing menopause with: [Close friend]",
    "18. Women can get sexually transmitted infections (STIs) after menopause:": "Women can get sexually transmitted infections (STIs) after menopause:",
    "17. Women can get pregnant during perimenopause:": "Women can get pregnant during perimenopause:",
    "16. Menopause may increase the risk of: (Select all possible options)": "Menopause may increase the risk of: (Select all possible options)",
    "11. At what age do you think women usually reach menopause?": "At what age do you think women usually reach menopause?",
    "9. Where did you learn about Menopause? (Select all possible options)": "Where did you learn about Menopause? (Select all possible options)",
    "13. What do you think are the symptoms of menopause? (Select all possible options)": "What do you think are the symptoms of menopause? (Select all possible options)"
}

# Create list of columns that can appear in the main dropdown
question_columns = list(column_display_names.keys())

# Multi-select question indices (replace with your actual indices)
multi_select_indices = [8, 12, 15]
multi_select_columns = [df.columns[i] for i in multi_select_indices]

# Columns for cross-distribution charts (replace with your actual indices)
cross_columns = df.columns[[3, 30, 6, 7, 1, 2]]

# -------------------------------
# 🎨 Global color palette
# -------------------------------
COLOR_SEQUENCE = [
    "#5DA5DA",  # bright blue
    "#F17C67",  # coral
    "#B276B2",  # purple
    "#60BD68",  # green
    "#FF9DA7",  # pink
    "#FFBE7D",  # peach
    "#4D4D4D",  # charcoal
    "#B2912F",  # mustard
]

PRIMARY = "#F17C67"     
SECONDARY = "#5DA5DA" 
ACCENT = "#B276B2"       

# -------------------------------
# 3️⃣ Streamlit UI
# -------------------------------
st.set_page_config(layout="wide")
st.title("MenoGlobal Mexico Survey Dashboard")

# Dropdown to select main question using friendly names
selected_question = st.selectbox(
    "Select a survey question:", 
    options=[column_display_names[col] for col in question_columns]
)

# Map back friendly name to raw column name
raw_selected_question = {v: k for k, v in column_display_names.items()}[selected_question]

# -------------------------------
# 4️⃣ Helper function to prepare counts with 'Other'
# -------------------------------
def prepare_counts(series, min_count=5):
    counts = series.value_counts().reset_index()
    counts.columns = [series.name, "count"]
    counts[series.name] = counts.apply(
        lambda row: row[series.name] if row["count"] >= min_count else "Other", axis=1
    )
    counts = counts.groupby(series.name, as_index=False)["count"].sum()
    counts["percent"] = counts["count"] / counts["count"].sum() * 100
    return counts

# -------------------------------
# 5️⃣ Main horizontal percentage bar chart
# -------------------------------
series = df[raw_selected_question].dropna()

# Explode multi-select answers
if raw_selected_question in multi_select_columns:
    series = series.str.split(", ").explode()

main_counts = pd.DataFrame({
    "Answer": series.value_counts().index,
    "count": series.value_counts().values
})
main_counts["percent"] = main_counts["count"] / main_counts["count"].sum() * 100

fig_main = px.bar(
    main_counts,
    x="percent",
    y="Answer",
    orientation="h",
    text=main_counts.apply(lambda r: f"{r['count']} ({r['percent']:.0f}%)", axis=1),
)

fig_main.update_layout(
    yaxis_title=None,
    xaxis_title="Percent",
    yaxis={"categoryorder": "total ascending"},
    margin=dict(l=150, r=150, t=50, b=50),
    font=dict(family="Arial, sans-serif", size=16, color="black"),
    xaxis=dict(range=[0, main_counts["percent"].max()*1.2])
)

fig_main.update_traces(
    marker_color="#FFBE7D",
    textposition="outside",
    textfont_size=14
)

st.plotly_chart(fig_main, use_container_width=True)

# -------------------------------
# 6️⃣ Filter df based on selected bar
# -------------------------------
if raw_selected_question in multi_select_columns:
    unique_options = series.dropna().unique()
else:
    unique_options = df[raw_selected_question].dropna().unique()

selected_bar = st.selectbox(
    f"Filter {selected_question} by value (or show all)", 
    options=["All"] + list(unique_options)
)

filtered_df = df.copy()
if selected_bar != "All":
    if raw_selected_question in multi_select_columns:
        filtered_df = filtered_df[filtered_df[raw_selected_question].str.contains(selected_bar, na=False)]
    else:
        filtered_df = filtered_df[filtered_df[raw_selected_question] == selected_bar]

# -------------------------------
# 7️⃣ Cross-distribution charts (unchanged from your original script)
# -------------------------------
st.subheader("Demographic profiles of respondents")

# Heights
chart_height = 450
tall_chart_height = chart_height * 2

# Chart configuration
chart_config = [
    {"col": cross_columns[0], "type": "hist", "title": "Age"},                  # 1st chart
    {"col": cross_columns[1], "type": "bar_h", "title": "City", "tall": True},  # 2nd chart tall
    {"col": cross_columns[2], "type": "pie", "title": "Sex"},                   # 3rd chart
    {"col": cross_columns[3], "type": "pie", "title": "Gender Identity"},       # 4th chart
    {"col": cross_columns[4], "type": "bar_v", "title": "Role at University"},  # 5th chart
    {"col": cross_columns[5], "type": "bar_h", "title": "Area of Study"},       # 6th chart full width
]

# -------------------------------
# Section 1: First three graphs
# -------------------------------
col1, col2 = st.columns(2)

# First chart (Age) - left column
series = filtered_df[chart_config[0]["col"]].dropna()
fig = px.histogram(series, nbins=200, title=chart_config[0]["title"], color_discrete_sequence=[SECONDARY])
fig.update_layout(showlegend=False, height=chart_height, yaxis_title=None, xaxis_title=None, font=dict(size=14), margin=dict(l=40,r=40,t=50,b=40))
col1.plotly_chart(fig, use_container_width=True)

# Second chart (City) - right column, tall
series = filtered_df[chart_config[1]["col"]].dropna()
counts = prepare_counts(series)
fig = px.bar(counts, x="percent", y=chart_config[1]["col"], orientation="h", title=chart_config[1]["title"],
             text=counts.apply(lambda r: f"{r['count']} ({r['percent']:.0f}%)", axis=1),
             color=chart_config[1]["col"], color_discrete_sequence=COLOR_SEQUENCE)
fig.update_traces(textposition="outside", textfont_size=14)
fig.update_layout(xaxis=dict(range=[0, counts["percent"].max()*1.2]),showlegend=False, yaxis_title=None, height=tall_chart_height, yaxis={"categoryorder": "total ascending"}, margin=dict(l=160,r=40,t=50,b=40))
col2.plotly_chart(fig, use_container_width=True)

# Third chart (Sex) - left column below Age
series = filtered_df[chart_config[2]["col"]].dropna()
counts = prepare_counts(series)
fig = px.pie(counts, names=chart_config[2]["col"], values="count", hole=0.3, title=chart_config[2]["title"],
             color=chart_config[2]["col"], color_discrete_sequence=COLOR_SEQUENCE)
fig.update_layout(height=chart_height, margin=dict(l=20,r=20,t=50,b=80), font=dict(size=14))
col1.plotly_chart(fig, use_container_width=True)
fig.update_traces(
    text=counts.apply(lambda r: f"{r['count']} ({r['percent']:.0f}%)", axis=1),
    textposition="inside",
    textinfo="text"  # <-- only display your custom text
)

# -------------------------------
# Section 2: Next two graphs side-by-side
# -------------------------------
col3, col4 = st.columns(2)

import textwrap

def wrap_label(s, width=40):
    """Wrap long labels for legend or y-axis readability."""
    return "<br>".join(textwrap.wrap(str(s), width))

for i, cfg in enumerate(chart_config[3:5]):  # Gender Identity and Role at University
    series = filtered_df[cfg["col"]].dropna()

    if cfg["type"] == "pie":
        counts = prepare_counts(series)
        # Wrap legend labels only
        counts["legend_label"] = counts[cfg["col"]].apply(lambda x: wrap_label(x, 40))

        fig = px.pie(
            counts,
            names="legend_label",          # wrapped labels for legend
            values="count",
            hole=0.3,
            title=cfg["title"],
            color="legend_label",
            color_discrete_sequence=COLOR_SEQUENCE,
            hover_data=[cfg["col"], "count", "percent"]  # list, not dict
        )
        fig.update_traces(
            text=counts.apply(lambda r: f"{r['count']} ({r['percent']:.0f}%)", axis=1),
            textposition="inside",
            textinfo="text"  # <-- only display your custom text
        )

        fig.update_layout(
            height=chart_height,
            margin=dict(l=20, r=20, t=50, b=80),
            font=dict(size=14),
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.05,
                title=None,
                font=dict(size=12)
            )
        )

    elif cfg["type"] == "bar_v":
        counts = prepare_counts(series)
        # Wrap long y-axis labels
        counts["wrapped_label"] = counts[cfg["col"]].apply(lambda x: wrap_label(x, 30))

        # Create the bar chart with data labels
        fig = px.bar(
            counts,
            x="percent",
            y="wrapped_label",
            title=cfg["title"],
            orientation="h",
            color="wrapped_label",
            color_discrete_sequence=COLOR_SEQUENCE,
            hover_data=[cfg["col"], "count", "percent"],  # show full info on hover
            text=counts.apply(lambda r: f"{r['count']} ({r['percent']:.0f}%)", axis=1)  # show count + percent
        )

        # Position the text outside the bars
        fig.update_traces(textposition="outside")

        fig.update_layout(
            height=chart_height,
            xaxis=dict(range=[0, counts["percent"].max()*1.2]),
            xaxis_title="percent",
            yaxis_title=None,
            yaxis={"categoryorder": "total ascending"},
            font=dict(size=14),
            margin=dict(l=160, r=40, t=50, b=40),
            showlegend=False  # hide redundant legend
        )


    # Plot in the appropriate column
    if i == 0:
        col3.plotly_chart(fig, use_container_width=True)
    else:
        col4.plotly_chart(fig, use_container_width=True)


# -------------------------------
# Section 3: Last graph full width
# -------------------------------
series = filtered_df[chart_config[5]["col"]].dropna()
counts = prepare_counts(series)

# Sort by percent descending for bars
counts = counts.sort_values("percent", ascending=False)

fig = px.bar(
    counts,
    x="percent",
    y=chart_config[5]["col"],  # use original column for bar positions
    orientation="h",
    title=chart_config[5]["title"],
    text=counts.apply(lambda r: f"{r['count']} ({r['percent']:.0f}%)", axis=1),
    color=chart_config[5]["col"],  # no wrapping, legend uses original labels
    color_discrete_sequence=COLOR_SEQUENCE,
    hover_data=[chart_config[5]["col"], "count", "percent"]
)

# Position text outside bars
fig.update_traces(
    textposition="outside",
    textfont_size=14,
    hovertemplate="%{customdata[0]}: %{customdata[1]} (%{customdata[2]:.0f}%)"
)

# Hide y-axis labels and title, place legend below
fig.update_layout(
    height=chart_height,
    yaxis=dict(title=None, showticklabels=False),
    xaxis_title=None,
    font=dict(size=14),
    margin=dict(l=40, r=40, t=50, b=120),  # more space at bottom
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.3,       # adjust as needed
        xanchor="left",
        x=0,          # align left
        title=None,
        font=dict(size=14)
    )    

)


st.plotly_chart(fig, use_container_width=True)
