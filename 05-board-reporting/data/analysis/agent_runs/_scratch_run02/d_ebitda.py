import pandas as pd
from pathlib import Path
D = Path(r"C:\Users\luigi\Dropbox\Archivio famiglia\Hapax\Case Studies\05 Board Reporting\data")
pd.set_option("display.width", 260, "display.max_columns", 40, "display.max_rows", 400)
pnl=pd.read_csv(D/"pnl_monthly.csv"); bud=pd.read_csv(D/"budget_pnl_monthly.csv")
opx=pd.read_csv(D/"opex_monthly.csv"); bopx=pd.read_csv(D/"budget_opex_monthly.csv")

def build(pl, op):
    p=pl.groupby("month",as_index=False).agg(net=("net_revenue","sum"),gp=("gross_profit","sum"),
        mat=("material_cost","sum"),vol=("volume_units","sum"),gross=("gross_revenue","sum"),promo=("promo_discounts","sum"))
    o=op.groupby("month",as_index=False).agg(sm=("sales_marketing","sum"),ad=("admin_general","sum"),oi=("other_income","sum"))
    m=p.merge(o,on="month"); m["ebitda"]=m.gp-m.sm-m.ad+m.oi; m["ebitda_und"]=m.ebitda-m.oi
    return m
A=build(pnl,opx); B=build(bud,bopx)
M=A.merge(B,on="month",suffixes=("_a","_b"))
M["year"]=M.month.str[:4]
M["ebitda_miss"]=M.ebitda_a-M.ebitda_b
M["ebitda_und_miss"]=M.ebitda_und_a-M.ebitda_b   # underlying vs budget (budget oi=0)
print("=== COMPANY monthly EBITDA: actual, underlying, budget, miss%, underlying miss% ===")
M["miss_pct"]=M.ebitda_miss/M.ebitda_b; M["und_miss_pct"]=M.ebitda_und_miss/M.ebitda_b
print(M[["month","ebitda_a","ebitda_und_a","ebitda_b","ebitda_miss","miss_pct","und_miss_pct","oi_a"]].round(3).to_string(index=False))

print("\n=== ANNUAL company ===")
ann=M.groupby("year").agg(net_a=("net_a","sum"),net_b=("net_b","sum"),gp_a=("gp_a","sum"),gp_b=("gp_b","sum"),
    sm_a=("sm_a","sum"),sm_b=("sm_b","sum"),ad_a=("ad_a","sum"),ad_b=("ad_b","sum"),oi_a=("oi_a","sum"),
    ebitda_a=("ebitda_a","sum"),ebitda_und_a=("ebitda_und_a","sum"),ebitda_b=("ebitda_b","sum"))
ann["gp_miss"]=ann.gp_a-ann.gp_b; ann["sm_over"]=ann.sm_a-ann.sm_b; ann["ad_over"]=ann.ad_a-ann.ad_b
ann["ebitda_miss"]=ann.ebitda_a-ann.ebitda_b; ann["und_miss"]=ann.ebitda_und_a-ann.ebitda_b
print(ann[["net_a","net_b","gp_a","gp_b","gp_miss","sm_over","ad_over","oi_a","ebitda_a","ebitda_und_a","ebitda_b","ebitda_miss","und_miss"]].round(0).to_string())

# ---- Quantify discount escalation cost: if 2025 disc rate held at 2024 BU average ----
p=pnl.copy(); p["year"]=p.month.str[:4]
d24=pnl.assign(year=pnl.month.str[:4]).query("year=='2024'").groupby("bu").apply(
    lambda x:x.promo_discounts.sum()/x.gross_revenue.sum(),include_groups=False).rename("dr24")
p25=p[p.year=="2025"].merge(d24,on="bu")
# counterfactual promo at 2024 rate, extra discount given = actual promo - gross*dr24
p25["extra_disc"]=p25.promo_discounts - p25.gross_revenue*p25.dr24
print("\n=== Extra promo discount in 2025 vs holding 2024 BU discount rate (EUR) ===")
print(p25.groupby("bu").extra_disc.sum().round(0).to_string())
print("Company total extra discount 2025: %.0f" % p25.extra_disc.sum())
# same by line
print("\nExtra discount by line (company, vs 2024 line rate):")
dl24=pnl.assign(year=pnl.month.str[:4]).query("year=='2024'").groupby("line").apply(
    lambda x:x.promo_discounts.sum()/x.gross_revenue.sum(),include_groups=False).rename("dr24l")
pl25=p[p.year=="2025"].merge(dl24,on="line"); pl25["extra"]=pl25.promo_discounts-pl25.gross_revenue*pl25.dr24l
print(pl25.groupby("line").extra.sum().round(0).to_string())
