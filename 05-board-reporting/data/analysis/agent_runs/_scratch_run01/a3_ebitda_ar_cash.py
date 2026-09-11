import pandas as pd, numpy as np
from pathlib import Path
import sys
sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 260); pd.set_option("display.max_columns", 40)
pd.set_option("display.float_format", lambda x: f"{x:,.2f}")
DATA = Path(__file__).resolve().parents[3]
pnl = pd.read_csv(DATA/"pnl_monthly.csv")
bud = pd.read_csv(DATA/"budget_pnl_monthly.csv")
opex = pd.read_csv(DATA/"opex_monthly.csv")
bopex = pd.read_csv(DATA/"budget_opex_monthly.csv")
wc = pd.read_csv(DATA/"working_capital_monthly.csv")
rc = pd.read_csv(DATA/"receivables_by_customer_monthly.csv")
cm = pd.read_csv(DATA/"customer_master.csv")
cash = pd.read_csv(DATA/"cash_monthly.csv")
crev = pd.read_csv(DATA/"customer_revenue_monthly.csv")
def secn(t): print("\n"+"="*80+"\n"+t+"\n"+"="*80)

# EBITDA reconstruction: gp(sum lines) - S&M - admin + other_income
gp = pnl.groupby(["month","bu"]).gross_profit.sum().reset_index()
gpb = bud.groupby(["month","bu"]).gross_profit.sum().reset_index().rename(columns={"gross_profit":"gp_bud"})
e = gp.merge(opex,on=["month","bu"]).merge(gpb,on=["month","bu"]).merge(
    bopex,on=["month","bu"],suffixes=("","_bud"))
e["ebitda"] = e.gross_profit - e.sales_marketing - e.admin_general + e.other_income
e["ebitda_bud"] = e.gp_bud - e.sales_marketing_bud - e.admin_general_bud + e.other_income_bud
e["year"]=e.month.str[:4]

secn("VERIFY EBITDA vs report (Nordics 2025-01 should be 704,208; company Apr reported 3,394,941)")
print(e[(e.month=="2025-01")&(e.bu=="Nordics")][["gross_profit","sales_marketing","admin_general","other_income","ebitda"]])
comp_apr = e[e.month=="2025-04"].ebitda.sum()
print("Company Apr2025 reported EBITDA:", comp_apr)
print("Company Apr2025 other_income total:", e[e.month=="2025-04"].other_income.sum())

secn("CLUSTER 4 — EBITDA vs budget miss decomposition by BU (FY2025) and where it comes from")
fy = e[e.year=="2025"].groupby("bu").agg(
    gp=("gross_profit","sum"), gp_bud=("gp_bud","sum"),
    sm=("sales_marketing","sum"), sm_bud=("sales_marketing_bud","sum"),
    admin=("admin_general","sum"), admin_bud=("admin_general_bud","sum"),
    oi=("other_income","sum"), oi_bud=("other_income_bud","sum"),
    ebitda=("ebitda","sum"), ebitda_bud=("ebitda_bud","sum")).reset_index()
fy["ebitda_var"]=fy.ebitda-fy.ebitda_bud
fy["gp_var"]=fy.gp-fy.gp_bud
fy["sm_var"]=-(fy.sm-fy.sm_bud)  # overspend reduces ebitda
fy["admin_var"]=-(fy.admin-fy.admin_bud)
fy["oi_var"]=fy.oi-fy.oi_bud
print(fy[["bu","ebitda","ebitda_bud","ebitda_var","gp_var","sm_var","admin_var","oi_var"]])
print("\nCompany FY2025 reported EBITDA:", fy.ebitda.sum(), " budget:", fy.ebitda_bud.sum(),
      " var:", fy.ebitda.sum()-fy.ebitda_bud.sum())
# ex the april one-off (other income actual)
print("Company FY2025 other_income actual total:", e[e.year=='2025'].other_income.sum(),
      " budget:", e[e.year=='2025'].other_income_bud.sum())
print("Underlying (ex other income) EBITDA var:", (fy.ebitda.sum()-fy.oi.sum())-(fy.ebitda_bud.sum()-fy.oi_bud.sum()))

secn("Material cost vs BUDGET — is Nordics material-cost flag a volume story? (actual vs budget volume & mat/unit)")
mv = pnl.groupby(["year:=year","bu"] if False else ["bu"]).size()  # noop
for bu in ["Nordics","Baltics & Poland"]:
    a = pnl[(pnl.month.str[:4]=="2025")&(pnl.bu==bu)]
    b = bud[(bud.month.str[:4]=="2025")&(bud.bu==bu)]
    print(f"{bu}: 2025 actual vol {a.volume_units.sum():,.0f} vs budget vol {b.volume_units.sum():,.0f} "
          f"({(a.volume_units.sum()/b.volume_units.sum()-1)*100:+.1f}%); "
          f"actual mat/u {a.material_cost.sum()/a.volume_units.sum():.4f} vs budget mat/u {b.material_cost.sum()/b.volume_units.sum():.4f}; "
          f"actual net/u {a.net_revenue.sum()/a.volume_units.sum():.4f} vs budget net/u {b.net_revenue.sum()/b.volume_units.sum():.4f}")

secn("CLUSTER 5 — Central Europe receivables build: by customer, 2024-12 vs 2025-12 closing AR")
ce = rc[rc.bu=="Central Europe"].merge(cm,on=["customer","bu"])
piv = ce.pivot_table(index=["customer","contractual_terms_days"],columns="month",values="receivables_closing")
cols=["2024-06","2024-12","2025-06","2025-09","2025-12"]
print(piv[cols].sort_values("2025-12",ascending=False))
print("\nCE total closing AR 2024-12:", ce[ce.month=='2024-12'].receivables_closing.sum(),
      " 2025-12:", ce[ce.month=='2025-12'].receivables_closing.sum())

secn("CE per-customer implied DSO (closing AR / (trailing12 net rev /365)) at 2025-12 vs their terms")
# monthly net rev per CE customer
cerev = crev[crev.bu=="Central Europe"].copy()
def trailing_dso(cust, upto):
    months = pd.period_range(end=pd.Period(upto,freq="M"), periods=12, freq="M").astype(str)
    rev = cerev[(cerev.customer==cust)&(cerev.month.isin(months))].net_revenue.sum()
    ar = rc[(rc.customer==cust)&(rc.bu=="Central Europe")&(rc.month==upto)].receivables_closing.iloc[0]
    return ar/(rev/365)
rows=[]
for cust in cerev.customer.unique():
    terms = cm[(cm.customer==cust)&(cm.bu=="Central Europe")].contractual_terms_days.iloc[0]
    rows.append((cust,terms,trailing_dso(cust,"2024-12"),trailing_dso(cust,"2025-12")))
dso=pd.DataFrame(rows,columns=["customer","terms","dso_2024-12","dso_2025-12"]).sort_values("dso_2025-12",ascending=False)
dso["chg"]=dso["dso_2025-12"]-dso["dso_2024-12"]
print(dso.to_string(index=False))

secn("CE collections vs closing AR trend (working_capital) 2025 monthly")
cewc = wc[wc.bu=="Central Europe"].copy()
print(cewc[cewc.month.str[:4]=="2025"][["month","receivables_opening","collections","receivables_closing"]].to_string(index=False))

secn("CLUSTER 6 — April one-off: other income by BU + investing cash flow")
print(opex[(opex.month=="2025-04")][["month","bu","other_income"]])
print("\nAll non-zero other_income rows across dataset:")
print(opex[opex.other_income!=0][["month","bu","other_income"]].to_string(index=False))
print("\nInvesting cash flow non-zero months:")
print(cash[cash.investing_cash_flow!=0][["month","operating_cash_flow","investing_cash_flow","cash_closing"]].to_string(index=False))

secn("CASH CONVERSION — 2025 operating CF vs reported & underlying EBITDA; AR build")
ocf25 = cash[cash.month.str[:4]=="2025"].operating_cash_flow.sum()
ebitda25 = e[e.year=="2025"].ebitda.sum()
oi25 = e[e.year=="2025"].other_income.sum()
print("2025 sum operating CF:", ocf25)
print("2025 reported EBITDA:", ebitda25, " underlying (ex OI):", ebitda25-oi25)
print("2025 investing CF:", cash[cash.month.str[:4]=='2025'].investing_cash_flow.sum())
# company AR build over 2025
arstart = wc[wc.month=="2025-01"].receivables_opening.sum()
arend = wc[wc.month=="2025-12"].receivables_closing.sum()
print("Company AR opening Jan2025:", arstart, " closing Dec2025:", arend, " build:", arend-arstart)
# AR build by BU
for bu in ["Nordics","Central Europe","Baltics & Poland"]:
    s=wc[(wc.bu==bu)&(wc.month=="2025-01")].receivables_opening.iloc[0]
    en=wc[(wc.bu==bu)&(wc.month=="2025-12")].receivables_closing.iloc[0]
    print(f"  {bu:18s} AR {s:,.0f} -> {en:,.0f}  build {en-s:+,.0f}")
print("\nCash closing Dec2024:", cash[cash.month=='2024-12'].cash_closing.iloc[0],
      " Dec2025:", cash[cash.month=='2025-12'].cash_closing.iloc[0])
