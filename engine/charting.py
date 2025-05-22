import matplotlib.pyplot as plt
import os


def render_trend_chart(trend_series, title="Spend Trend", ylabel="Spend ($)", filename="trend_chart.png"):
    plt.figure(figsize=(8, 5))
    trend_series.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel("Year")
    plt.xticks(rotation=0)
    plt.tight_layout()

    output_dir = "output_charts"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath)
    plt.close()
    return filepath