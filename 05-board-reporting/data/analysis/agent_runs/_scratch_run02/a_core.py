import pandas as pd
from pathlib import Path

D = Path(r"C:\Users\luigi\Dropbox\Archivio famiglia\Hapax\Case Studies\05 Board Reporting\data")
pd.set_option("display.width", 200, "display.max_columns", 30, "display.max_rows", 200)

pnl = pd.read_csv(D/"pnl_monthly.csv")
bud = pd.read_csv(D/"budget_pnl_monthly.csv")
for df in (pnl, bud):
    df["year"] = df["month"].str[:4]

def add_disc(df):
    df["disc_rate"] = df["promo_discounts"]/df["gross_revenue"]
    return df
pnl = add_disc(pnl); bud = add_disc(bud)

# ---- Cluster 1: seasonality. Company net revenue by month ----
comp = pnl.groupby("month", as_index=False).agg(net_revenue=("net_revenue","sum"),
       gross_revenue=("gross_revenue","sum"), promo=("promo_discounts","sum"),
       material=("material_cost","sum"), gp=("gross_profit","sum"), vol=("volume_units","sum"))
comp["gm_pct"] = comp["gp"]/comp["net_revenue"]
comp["disc_rate"] = comp["promo"]/comp["gross_revenue"]
print("=== COMPANY MONTHLY (net rev, gm%, disc rate) ===")
print(comp[["month","net_revenue","gm_pct","disc_rate"]].to_string(index=False))

# MoM
comp["mom"] = comp["net_revenue"].pct_change()
print("\n=== Company net revenue MoM ===")
print(comp[["month","net_revenue","mom"]].to_string(index=False))

# Jan vs Dec each year & YoY Jan
print("\nJan2024:", comp.loc[comp.month=="2024-01","net_revenue"].values,
      "Jan2025:", comp.loc[comp.month=="2025-01","net_revenue"].values,
      "Dec2024:", comp.loc[comp.month=="2024-12","net_revenue"].values)
