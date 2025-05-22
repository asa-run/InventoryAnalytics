import pandas as pd

def get_total_spend(df: pd.DataFrame, year: int, column: str, value: str) -> float:
    """Returns total spend for a given year, column, and value."""
    subset = df[(df[column].str.contains(value, case=False, na=False)) & (df["YEAR"] == year)]
    return subset["AMOUNT INVOICED"].sum()

def get_trend(df: pd.DataFrame, column: str, value: str, year_range: list) -> pd.Series:
    """Returns spend trend for a given value in a column across specified years."""
    subset = df[df[column].str.contains(value, case=False, na=False)]
    subset = subset[subset["YEAR"].isin(year_range)]
    return subset.groupby("YEAR")["AMOUNT INVOICED"].sum()

def get_unit_cost_summary(df: pd.DataFrame, column: str, value: str) -> pd.Series:
    """Returns average, min, max unit cost for a target."""
    subset = df[df[column].str.contains(value, case=False, na=False)].copy()
    subset["UNIT_COST"] = subset["AMOUNT INVOICED"] / subset["QUANTITY"]
    return subset["UNIT_COST"].describe()[["mean", "min", "max"]]

def get_supplier_unit_cost_extremes(df: pd.DataFrame, column: str, value: str) -> dict:
    """Returns suppliers with highest and lowest average unit cost for the target."""
    subset = df[df[column].str.contains(value, case=False, na=False)].copy()
    subset["UNIT_COST"] = subset["AMOUNT INVOICED"] / subset["QUANTITY"]
    grouped = subset.groupby("Supplier Name")["UNIT_COST"].mean()
    return {
        "lowest_supplier": grouped.idxmin(),
        "lowest_cost": round(grouped.min(), 2),
        "highest_supplier": grouped.idxmax(),
        "highest_cost": round(grouped.max(), 2)
    }

def get_unit_cost_trend_by_supplier(df: pd.DataFrame, column: str, value: str) -> pd.DataFrame:
    """Returns unit cost trend by year and supplier."""
    subset = df[df[column].str.contains(value, case=False, na=False)].copy()
    subset["UNIT_COST"] = subset["AMOUNT INVOICED"] / subset["QUANTITY"]
    return subset.groupby(["YEAR", "Supplier Name"])["UNIT_COST"].mean().unstack().round(2)