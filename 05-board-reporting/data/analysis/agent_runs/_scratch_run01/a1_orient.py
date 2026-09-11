import pandas as pd
from pathlib import Path
pd.set_option("display.width", 200); pd.set_option("display.max_columns", 30)
DATA = Path(__file__).resolve().parents[3]
pnl = pd.read_csv(DATA/"pnl_monthly.csv")
cm = pd.read_csv(DATA/"customer_master.csv")
print("BUs:", sorted(pnl.bu.unique()))
print("Lines:", sorted(pnl.line.unique()))
print("Months:", pnl.month.min(), "->", pnl.month.max(), "n=", pnl.month.nunique())
print("\ncustomer_master channels:", cm.channel.unique())
print("terms values:", sorted(cm.contractual_terms_days.unique()))
print("\ncustomers per BU:\n", cm.groupby("bu").customer.count())
print("\nfull customer_master:\n", cm.to_string())
