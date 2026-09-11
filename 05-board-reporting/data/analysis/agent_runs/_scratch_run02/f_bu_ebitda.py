import pandas as pd
from pathlib import Path
D = Path(r"C:\Users\luigi\Dropbox\Archivio famiglia\Hapax\Case Studies\05 Board Reporting\data")
pd.set_option("display.width", 260, "display.max_columns", 40, "display.max_rows", 200)
pnl=pd.read_csv(D/"pnl_monthly.csv"); bud=pd.read_csv(D/"budget_pnl_monthly.csv")
opx=pd.read_csv(D/"opex_monthly.csv"); bopx=pd.read_csv(D/"budget_opex_monthly.csv")

def bu_ann(pl,op):
    pl=pl.copy(); pl["year"]=pl.month.str[:4]; op=op.copy(); op["year"]=op.month.str[:4]
    g=pl.groupby(["year","bu"]).agg(net=("net_revenue","sum"),gp=("gross_profit","sum")).reset_index()
    o=op.groupby(["year","bu"]).agg(sm=("sales_marketing","sum"),ad=("admin_general","sum"),oi=("other_income","sum")).reset_index()
    m=g.merge(o,on=["year","bu"]); m["ebitda"]=m.gp-m.sm-m.ad+m.oi; m["ebitda_und"]=m.ebitda-m.oi
    m["gm"]=m.gp/m.net
    return m
A=bu_ann(pnl,opx); B=bu_ann(bud,bopx)
T=A.merge(B,on=["year","bu"],suffixes=("_a","_b"))
T["ebitda_miss"]=T.ebitda_a-T.ebitda_b
T["ebitda_und_miss"]=T.ebitda_und_a-T.ebitda_b
print("=== Per-BU annual: net rev, gm%, EBITDA actual/underlying/budget, miss ===")
print(T[["year","bu","net_a","gm_a","gm_b","ebitda_a","ebitda_und_a","ebitda_b","ebitda_und_miss"]].round(3).to_string(index=False))

# YoY EBITDA underlying by BU
print("\n=== EBITDA (underlying) YoY by BU ===")
p=T.pivot(index="bu",columns="year",values="ebitda_und_a")
p["chg"]=p["2025"]-p["2024"]; p["pct"]=p["chg"]/p["2024"]
print(p.round(3).to_string())

# revenue YoY by BU
print("\n=== Net revenue YoY by BU ===")
r=T.pivot(index="bu",columns="year",values="net_a"); r["chg"]=r["2025"]-r["2024"]; r["pct"]=r["chg"]/r["2024"]
print(r.round(3).to_string())
