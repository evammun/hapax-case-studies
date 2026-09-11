import pandas as pd
from pathlib import Path

DATA = Path(__file__).resolve().parents[3]  # .../05 Board Reporting/data
ANA = DATA / "analysis"

files = {
    "pnl_monthly": DATA / "pnl_monthly.csv",
    "budget_pnl_monthly": DATA / "budget_pnl_monthly.csv",
    "opex_monthly": DATA / "opex_monthly.csv",
    "budget_opex_monthly": DATA / "budget_opex_monthly.csv",
    "customer_master": DATA / "customer_master.csv",
    "customer_revenue_monthly": DATA / "customer_revenue_monthly.csv",
    "working_capital_monthly": DATA / "working_capital_monthly.csv",
    "receivables_by_customer_monthly": DATA / "receivables_by_customer_monthly.csv",
    "cash_monthly": DATA / "cash_monthly.csv",
    "kpi_monthly": ANA / "kpi_monthly.csv",
    "variances_monthly": ANA / "variances_monthly.csv",
    "pvm_fy2025": ANA / "pvm_fy2025.csv",
}

for name, p in files.items():
    df = pd.read_csv(p)
    print("=" * 70)
    print(name, "shape", df.shape)
    print("cols:", list(df.columns))
    print(df.head(3).to_string())
    print()
