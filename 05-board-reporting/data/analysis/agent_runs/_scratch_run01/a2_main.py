import pandas as pd, numpy as np
from pathlib import Path
import sys
sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 240); pd.set_option("display.max_columns", 40)
pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

DATA = Path(__file__).resolve().parents[3]
ANA = DATA/"analysis"
pnl = pd.read_csv(DATA/"pnl_monthly.csv")
bud = pd.read_csv(DATA/"budget_pnl_monthly.csv")
opex = pd.read_csv(DATA/"opex_monthly.csv")
bopex = pd.read_csv(DATA/"budget_opex_monthly.csv")
wc = pd.read_csv(DATA/"working_capital_monthly.csv")
cash = pd.read_csv(DATA/"cash_monthly.csv")

for d in (pnl,bud,opex,bopex,wc,cash):
    d["year"] = d["month"].str[:4]

def secn(t): print("\n"+"="*80+"\n"+t+"\n"+"="*80)

# ---------------------------------------------------------------
secn("1. SEASONALITY — company net revenue by month, 2024 vs 2025")
comp = pnl.groupby("month").net_revenue.sum()
tbl = pd.DataFrame({
    "2024": [comp.get(f"2024-{m:02d}",np.nan) for m in range(1,13)],
    "2025": [comp.get(f"2025-{m:02d}",np.nan) for m in range(1,13)],
}, index=[f"M{m:02d}" for m in range(1,13)])
tbl["YoY%"] = (tbl["2025"]/tbl["2024"]-1)*100
tbl["2024_MoM%"] = tbl["2024"].pct_change()*100
tbl["2025_MoM%"] = tbl["2025"].pct_change()*100
print(tbl)
print("\nDec2024:", comp.get("2024-12"), " Jan2025:", comp.get("2025-01"),
      " Jan25 vs Dec24 MoM%:", (comp.get("2025-01")/comp.get("2024-12")-1)*100)
print("Jan2024:", comp.get("2024-01"), " Jan2025 YoY%:", (comp.get("2025-01")/comp.get("2024-01")-1)*100)
# Was Dec-Jan drop also present entering 2024? we lack Dec2023, but check Nov->Dec build both years
print("Nov->Dec build 2024:", (comp.get('2024-12')/comp.get('2024-11')-1)*100, "%   2025:", (comp.get('2025-12')/comp.get('2025-11')-1)*100,"%")

# ---------------------------------------------------------------
secn("2. FY MARGIN BRIDGE by BU — 2024 vs 2025 (gross margin compression?)")
def fy(df, col, by):
    a = df[df.year=="2024"].groupby(by)[col].sum()
    b = df[df.year=="2025"].groupby(by)[col].sum()
    return a,b
for by in [["bu"]]:
    g = pnl.groupby(["year"]+by).agg(net=("net_revenue","sum"),
        gross=("gross_revenue","sum"), disc=("promo_discounts","sum"),
        mat=("material_cost","sum"), lab=("direct_labour","sum"),
        log=("logistics_cost","sum"), gp=("gross_profit","sum"),
        vol=("volume_units","sum")).reset_index()
    g["gm%"] = g.gp/g.net*100
    g["disc%ofgross"] = g.disc/g.gross*100
    g["mat%ofnet"] = g.mat/g.net*100
    g["net/unit"] = g.net/g.vol
    g["mat/unit"] = g.mat/g.vol
    g["gross/unit"] = g.gross/g.vol
    piv = g.pivot(index="bu", columns="year")
    for metric in ["net","gp","gm%","disc%ofgross","mat%ofnet","net/unit","mat/unit","gross/unit","vol"]:
        sub = piv[metric]
        sub = sub.assign(chg=(sub["2025"]-sub["2024"]), pct=(sub["2025"]/sub["2024"]-1)*100)
        print(f"\n--- {metric} ---")
        print(sub)

# company totals
secn("2b. COMPANY FY margins")
gc = pnl.groupby("year").agg(net=("net_revenue","sum"),gross=("gross_revenue","sum"),
    disc=("promo_discounts","sum"),mat=("material_cost","sum"),gp=("gross_profit","sum"),
    vol=("volume_units","sum"))
gc["gm%"]=gc.gp/gc.net*100; gc["disc%"]=gc.disc/gc.gross*100
gc["net/unit"]=gc.net/gc.vol; gc["mat/unit"]=gc.mat/gc.vol
print(gc)

# ---------------------------------------------------------------
secn("3. PER-UNIT: is material cost/unit rising (input inflation) or is net/unit falling (price erosion)?")
# by BU by line FY
gl = pnl.groupby(["year","bu","line"]).agg(net=("net_revenue","sum"),gross=("gross_revenue","sum"),
    disc=("promo_discounts","sum"),mat=("material_cost","sum"),vol=("volume_units","sum"),
    lp=("list_price_eur","mean")).reset_index()
gl["net/unit"]=gl.net/gl.vol; gl["mat/unit"]=gl.mat/gl.vol; gl["gross/unit"]=gl.gross/gl.vol
gl["disc%"]=gl.disc/gl.gross*100
for bu in ["Nordics","Baltics & Poland","Central Europe"]:
    print(f"\n### {bu}")
    for line in sorted(pnl.line.unique()):
        r24=gl[(gl.year=="2024")&(gl.bu==bu)&(gl.line==line)].iloc[0]
        r25=gl[(gl.year=="2025")&(gl.bu==bu)&(gl.line==line)].iloc[0]
        print(f"  {line:14s} vol {r24.vol:>9,.0f}->{r25.vol:>9,.0f} ({(r25.vol/r24.vol-1)*100:+5.1f}%) "
              f"list {r24.lp:5.2f}->{r25.lp:5.2f} gross/u {r24['gross/unit']:5.3f}->{r25['gross/unit']:5.3f} "
              f"net/u {r24['net/unit']:5.3f}->{r25['net/unit']:5.3f}({(r25['net/unit']/r24['net/unit']-1)*100:+5.1f}%) "
              f"mat/u {r24['mat/unit']:5.3f}->{r25['mat/unit']:5.3f}({(r25['mat/unit']/r24['mat/unit']-1)*100:+5.1f}%) "
              f"disc {r24['disc%']:4.1f}%->{r25['disc%']:4.1f}%")

# ---------------------------------------------------------------
secn("4. PROMO DISCOUNT rate by BU by month (2024 vs 2025)")
dd = pnl.groupby(["month","bu"]).agg(gross=("gross_revenue","sum"),disc=("promo_discounts","sum")).reset_index()
dd["disc%"]=dd.disc/dd.gross*100
for bu in ["Nordics","Baltics & Poland","Central Europe"]:
    s=dd[dd.bu==bu].set_index("month")["disc%"]
    row24=[s.get(f"2024-{m:02d}",np.nan) for m in range(1,13)]
    row25=[s.get(f"2025-{m:02d}",np.nan) for m in range(1,13)]
    print(f"{bu:18s} 2024 mean {np.nanmean(row24):.2f}%  2025 mean {np.nanmean(row25):.2f}%")
    print("   2024:", " ".join(f"{v:4.1f}" for v in row24))
    print("   2025:", " ".join(f"{v:4.1f}" for v in row25))
