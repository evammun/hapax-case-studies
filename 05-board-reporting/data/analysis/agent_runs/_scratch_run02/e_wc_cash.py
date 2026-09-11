import pandas as pd
from pathlib import Path
D = Path(r"C:\Users\luigi\Dropbox\Archivio famiglia\Hapax\Case Studies\05 Board Reporting\data")
pd.set_option("display.width", 260, "display.max_columns", 40, "display.max_rows", 500)
wc=pd.read_csv(D/"working_capital_monthly.csv")
rc=pd.read_csv(D/"receivables_by_customer_monthly.csv")
cm=pd.read_csv(D/"customer_master.csv")
cust_rev=pd.read_csv(D/"customer_revenue_monthly.csv")
cash=pd.read_csv(D/"cash_monthly.csv")

# ---- Central Europe receivables by customer: closing AR trend ----
ce=rc[rc.bu=="Central Europe"].merge(cm,on=["customer","bu"],how="left")
print("=== Central Europe: closing AR by customer, selected months ===")
piv=ce.pivot(index="month",columns="customer",values="receivables_closing")
print(piv.round(0).to_string())
print("\nCE customer terms:")
print(cm[cm.bu=="Central Europe"][["customer","channel","contractual_terms_days"]].to_string(index=False))

# CE customer monthly net revenue (to compute per-customer DSO-ish) & collections
print("\n=== CE closing AR Dec2024 vs Dec2025 by customer, with 2025 monthly net rev avg ===")
cerev=cust_rev[cust_rev.bu=="Central Europe"].copy(); cerev["year"]=cerev.month.str[:4]
rev25=cerev[cerev.year=="2025"].groupby("customer").net_revenue.mean().rename("avg_mo_netrev25")
ar_dec24=ce[ce.month=="2024-12"].set_index("customer").receivables_closing.rename("AR_Dec24")
ar_dec25=ce[ce.month=="2025-12"].set_index("customer").receivables_closing.rename("AR_Dec25")
coll25=ce[ce.year_x=="2025"].groupby("customer").collections.sum().rename("coll25") if "year_x" in ce else None
t=pd.concat([ar_dec24,ar_dec25,rev25],axis=1)
t["AR_change"]=t.AR_Dec25-t.AR_Dec24
t["mo_of_rev_Dec25"]=t.AR_Dec25/t.avg_mo_netrev25
print(t.round(0).to_string())

# collections ratio per CE customer 2025: collections / (opening+charges)...
ce2=ce.copy(); ce2["year"]=ce2.month.str[:4]
print("\n=== CE per-customer: sum collections 2024 vs 2025, and closing AR growth ===")
for yr in ["2024","2025"]:
    s=ce2[ce2.year==yr].groupby("customer").agg(coll=("collections","sum")).rename(columns={"coll":f"coll_{yr}"})
    print(s.round(0).to_string())

# ---- Cash: operating CF sum, investing, closing ----
cash["year"]=cash.month.str[:4]
print("\n=== CASH annual ===")
print(cash.groupby("year").agg(op_cf=("operating_cash_flow","sum"),inv_cf=("investing_cash_flow","sum"),
    close=("cash_closing","last")).round(0).to_string())
print("\nInvesting CF non-zero months:")
print(cash[cash.investing_cash_flow!=0][["month","investing_cash_flow"]].to_string(index=False))

# ---- Company DSO check via working capital totals ----
wc["year"]=wc.month.str[:4]
comp_wc=wc.groupby("month").agg(closing=("receivables_closing","sum"),coll=("collections","sum"),opening=("receivables_opening","sum"))
print("\n=== Company receivables closing by month ===")
print(comp_wc.round(0).to_string())
