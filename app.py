from classifier.question_classifier import classify_question
from engine.data_loader import load_invoice_data
from engine import analytics_engine as ae
from engine.schema_mapping import COLUMN_ALIASES
from engine.charting import render_trend_chart

df = load_invoice_data()
previous_question = ""

print("\n📊 Invoice Analytics CLI — Type 'exit' to quit\n")

while True:
    q = input("🔎 Ask: ").strip()
    if q.lower() in ['exit', 'quit']:
        break

    intent = classify_question(q, previous_question)

    # Patch column name if needed
    col = intent.get("column")
    if col in COLUMN_ALIASES:
        intent["column"] = COLUMN_ALIASES[col]
    elif col not in df.columns:
        print(f"⚠️ Column '{col}' not found in data. Please update schema mapping.")
        continue

    previous_question = q  # Save for next round
    print(f"🧠 Intent: {intent}\n")

    required_keys = {
        "total_spend": ["column", "target"],  # removed 'year'
        "trend": ["column", "target", "year_range"],
        "unit_cost": ["column", "target"],
        "extremes": ["column", "target"],
        "unit_cost_trend": ["column", "target"],
    }

    missing = [k for k in required_keys.get(intent["intent"], []) if k not in intent]
    if missing:
        print(f"⚠️ Missing fields in intent: {missing}")
        print(f"Intent received: {intent}\n")
        continue

    try:
        if intent["intent"] == "total_spend":
            if not intent.get("year"):
                all_years = sorted(df["YEAR"].unique())
                all_years = [int(y) for y in all_years]  # convert np.int32 to plain Python int
                print(f"📌 Year not specified — using total across all years: {all_years}")
                intent["year_range"] = all_years

            if "year_range" in intent:
                total = sum(
                    ae.get_total_spend(df, year=year, column=intent["column"], value=intent["target"])
                    for year in intent["year_range"]
                )
            else:
                total = ae.get_total_spend(df, year=intent["year"], column=intent["column"], value=intent["target"])

            print(f"💰 Total Spend: ${total:,.2f}\n")

        elif intent["intent"] == "trend":
            if not intent.get("year_range"):
                intent["year_range"] = sorted(df["YEAR"].unique().tolist())
                print(f"📌 Year range not specified — using all available years: {intent['year_range']}")

            trend = ae.get_trend(df, column=intent["column"], value=intent["target"], year_range=intent["year_range"])
            print("📈 Trend (Spend by Year):")
            trend_formatted = trend.apply(lambda x: f"${x:,.0f}")
            # print(trend_formatted.to_string())
            chart_path = render_trend_chart(trend, title=f"Trend for {intent['target']}")
            print(f"📊 Trend chart saved: {chart_path}")

        elif intent["intent"] == "unit_cost":
            stats = ae.get_unit_cost_summary(df, column=intent["column"], value=intent["target"])
            print(f"📊 Unit Cost Summary:\n{stats.to_string()}\n")

        elif intent["intent"] == "extremes":
            result = ae.get_supplier_unit_cost_extremes(df, column=intent["column"], value=intent["target"])
            print(f"📉 Lowest: {result['lowest_supplier']} (${result['lowest_cost']})")
            print(f"📈 Highest: {result['highest_supplier']} (${result['highest_cost']})\n")

        elif intent["intent"] == "unit_cost_trend":
            table = ae.get_unit_cost_trend_by_supplier(df, column=intent["column"], value=intent["target"])
            print(f"📊 Unit Cost Trend by Year and Supplier:\n{table.to_string()}\n")

        elif intent["intent"] == "optimization":
            print(f"💡 Optimization tip for {intent['target']}:\n"
                  f"- Consolidate purchases\n- Review outliers\n- Negotiate contracts\n")

        else:
            print("❓ Unsupported or unknown intent.\n")

    except Exception as e:
        print(f"⚠️ Error: {e}\n")