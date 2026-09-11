import pandas as pd
from pathlib import Path
D = Path(r"C:\Users\luigi\Dropbox\Archivio famiglia\Hapax\Case Studies\05 Board Reporting\data")
pd.set_option("display.width", 260, "display.max_columns", 40, "display.max_rows", 400)
pnl = pd.read_csv(D/"pnl_monthly.csv"); bud=pd.read_csv(D/"budget_pnl_monthly.csv")
opx = pd.read_csv(D/"opex_monthly.csv"); bopx=pd.read_csv(D/"budget_opex_monthly.csv")
for d in (pnl,bud): d["year"]=d["month"].str[:4]

# BU x line discount rate 2025 monthly for Home Care + material unit cost by line/BU by year
m = pnl.copy(); m["disc_rate"]=m["promo_discounts"]/m["gross_revenue"]; m["mat_u"]=m["material_cost"]/m["volume_units"]
print("=== Home Care discount rate by BU, 2025 ===")
hc=m[(m.line=="Home Care")&(m.year=="2025")]
print(hc.pivot(index="month",columns="bu",values="disc_rate").round(4).to_string())

print("\n=== Material cost per unit by BU x line, 2024 vs 2025 ===")
mu=pnl.groupby([pnl.month.str[:4],"bu","line"]).apply(lambda x:(x.material_cost.sum()/x.volume_units.sum()),include_groups=False)
print(mu.unstack(0).round(4).to_string())

# Budget: discount rate & gm assumed vs actual, company & BU by year
def agg(df):
    return df.groupby([df.month.str[:4],"bu"]).agg(gross=("gross_revenue","sum"),promo=("promo_discounts","sum"),
        net=("net_revenue","sum"),mat=("material_cost","sum"),gp=("gross_profit","sum"),vol=("volume_units","sum"))
a=agg(pnl); b=agg(bud)
comp=pd.DataFrame({"act_disc":a.promo/a.gross,"bud_disc":b.promo/b.gross,"act_gm":a.gp/a.net,"bud_gm":b.gp/b.net,
    "act_matu":a.mat/a.vol,"bud_matu":b.mat/b.vol,"act_netu":a.net/a.vol,"bud_netu":b.net/b.vol})
print("\n=== ACTUAL vs BUDGET: disc rate, gm, unit mat, unit net -- by BU by year ===")
print(comp.round(4).to_string())

# ---- OPEX: S&M, admin vs budget, EBITDA build ----
o=opx.merge(bopx,on=["month","bu"],suffixes=("_a","_b")); o["year"]=o["month"].str[:4]
osum=o.groupby(["year","bu"]).agg(sm_a=("sales_marketing_a","sum"),sm_b=("sales_marketing_b","sum"),
    ad_a=("admin_general_a","sum"),ad_b=("admin_general_b","sum"),oi_a=("other_income_a","sum"),oi_b=("other_income_b","sum"),
    fte_a=("headcount_fte_a","mean"),fte_b=("headcount_fte_b","mean"))
print("\n=== OPEX actual vs budget by BU by year (S&M, admin, other income, avg FTE) ===")
print(osum.round(0).to_string())

# EBITDA build by BU by year: gp - sm - admin + other_income
gp=pnl.groupby([pnl.month.str[:4],"bu"]).gross_profit.sum().rename("gp_a")
gpb=bud.groupby([bud.month.str[:4],"bu"]).gross_profit.sum().rename("gp_b")
o2=o.groupby([o.year,"bu"]).agg(sm_a=("sales_marketing_a","sum"),sm_b=("sales_marketing_b","sum"),
    ad_a=("admin_general_a","sum"),ad_b=("admin_general_b","sum"),oi_a=("other_income_a","sum"),oi_b=("other_income_b","sum"))
E=o2.join(gp).join(gpb)
E["ebitda_a"]=E.gp_a-E.sm_a-E.ad_a+E.oi_a; E["ebitda_b"]=E.gp_b-E.sm_b-E.ad_b+E.oi_b
E["ebitda_a_underlying"]=E.ebitda_a-E.oi_a
E["gp_miss"]=E.gp_a-E.gp_b; E["sm_over"]=E.sm_a-E.sm_b; E["ad_over"]=E.ad_a-E.ad_b; E["ebitda_miss"]=E.ebitda_a-E.ebitda_b
print("\n=== EBITDA build & miss decomposition by BU by year ===")
print(E[["gp_a","gp_b","gp_miss","sm_over","ad_over","oi_a","ebitda_a","ebitda_b","ebitda_miss","ebitda_a_underlying"]].round(0).to_string())
print("\nCompany 2025 totals:")
print(E.loc["2025"][["gp_miss","sm_over","ad_over","oi_a","ebitda_a","ebitda_b","ebitda_miss","ebitda_a_underlying"]].sum().round(0))
print("Company 2024 totals:")
print(E.loc["2024"][["gp_miss","sm_over","ad_over","oi_a","ebitda_a","ebitda_b","ebitda_miss","ebitda_a_underlying"]].sum().round(0))
