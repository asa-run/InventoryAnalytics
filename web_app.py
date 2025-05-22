import streamlit as st
from classifier.question_classifier import classify_question
from engine.data_loader import load_invoice_data
from engine import analytics_engine as ae
from engine.charting import render_trend_chart
from engine.schema_mapping import COLUMN_ALIASES
import io
import pandas as pd

# Load data
df = load_invoice_data()
st.title("Alpha Omega Invoice Analytics (Using Synthetic Data)")

# Initialize state
if "previous_question" not in st.session_state:
    st.session_state.previous_question = ""
if "last_response" not in st.session_state:
    st.session_state.last_response = None
if "reset_input_flag" not in st.session_state:
    st.session_state.reset_input_flag = False

# Handle input reset cleanly
if st.session_state.reset_input_flag:
    st.session_state.reset_input_flag = False
    st.rerun()

# Main UI
response_area = st.empty()
user_input = st.text_input("Ask a question:", key="user_input")
submitted = st.button("Submit")

if not (submitted and user_input):
    with response_area.container():
        if st.session_state.last_response:
            r = st.session_state.last_response

            # Display results based on response type
            if r["type"] == "chart":
                st.image(r["path"], caption=r["title"])
            elif r["type"] == "metric":
                st.write(r["text"])
                st.metric(r["label"], r["value"])
            elif r["type"] == "table":
                st.write(r["text"])
                st.dataframe(r["data"])

            # ✅ Download CSV if available
            if "data" in r and isinstance(r["data"], pd.DataFrame):
                csv = r["data"].to_csv(index=False)
                st.download_button(
                    label="📥 Download underlying data as CSV",
                    data=csv,
                    file_name="analysis_result.csv",
                    mime="text/csv"
                )
        else:
            st.markdown(
                "<span style='color:gray;'>Awaiting input... Ask a question to see results here.</span>",
                unsafe_allow_html=True
            )

else:
    intent = classify_question(user_input, previous_question=st.session_state.previous_question)
    st.session_state.previous_question = user_input

    col = intent.get("column")
    if col in COLUMN_ALIASES:
        intent["column"] = COLUMN_ALIASES[col]

    with response_area.container():
        if False:
            st.write("🔍 Detected intent:", intent)

        try:
            if intent["intent"] == "trend":
                if not intent.get("year_range"):
                    intent["year_range"] = sorted(df["YEAR"].unique().tolist())
                trend = ae.get_trend(df, column=intent["column"], value=intent["target"],
                                     year_range=intent["year_range"])
                chart_path = render_trend_chart(trend, title=f"Trend for {intent['target']}")
                st.image(chart_path)
                st.session_state.last_response = {
                    "type": "chart",
                    "path": chart_path,
                    "title": f"Trend for {intent['target']}",
                    "data": trend.reset_index()
                }

            elif intent["intent"] == "total_spend":
                if not intent.get("year"):
                    intent["year_range"] = sorted(df["YEAR"].unique())
                    total = sum(
                        ae.get_total_spend(df, year=yr, column=intent["column"], value=intent["target"])
                        for yr in intent["year_range"]
                    )
                    label = "Total Spend (All Years)"
                    df_total = pd.DataFrame([{
                        "Year": yr,
                        "Spend": ae.get_total_spend(df, year=yr, column=intent["column"], value=intent["target"])
                    } for yr in intent["year_range"]])
                    explanation = f"The total spend for **{intent['target']}** across all years is:"
                else:
                    year = intent["year"]
                    total = ae.get_total_spend(df, year=year, column=intent["column"], value=intent["target"])
                    label = f"Total Spend ({year})"
                    df_total = pd.DataFrame([{
                        "Year": year,
                        "Spend": total
                    }])
                    explanation = f"The total spend for **{intent['target']}** in {year} is:"
                st.write(explanation)
                st.metric(label, f"${total:,.2f}")
                st.session_state.last_response = {
                    "type": "metric",
                    "label": label,
                    "value": f"${total:,.2f}",
                    "data": df_total,
                    "text": explanation
                }

            elif intent["intent"] == "unit_cost":
                stats = ae.get_unit_cost_summary(df, column=intent["column"], value=intent["target"])
                explanation = f"Unit cost summary for **{intent['target']}**:"
                st.write(explanation)
                st.dataframe(stats)
                st.session_state.last_response = {
                    "type": "table",
                    "data": stats,
                    "text": explanation
                }

        except Exception as e:
            st.error(f"Error: {e}")
            st.session_state.last_response = None

    # Set reset flag (safe)
    st.session_state.reset_input_flag = True