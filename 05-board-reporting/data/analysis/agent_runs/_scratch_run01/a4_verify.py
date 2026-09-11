import pandas as pd, numpy as np
from pathlib import Path
import sys; sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width",240); pd.set_option("display.float_format",lambda x:f"{x:,.2f}")
DATA=Path(__file__).resolve().parents[3]
pnl=pd.read_csv(DATA/"pnl_monthly.csv"); opex=pd.read_csv(DATA/"opex_monthly.csv")
cash=pd.read_csv(DATA/"cash_monthly.csv")
gp=pnl.groupby(["month","bu"]).gross_profit.sum().reset_index()
e=gp.merge(opex,on=["month","bu"])
e["ebitda"]=e.gross_profit-e.sales_marketing-e.admin_general+e.other_income
e["year"]=e.month.str[:4]

print("=== EBITDA YoY by BU: reported vs underlying (ex other income) ===")
for bu in ["Nordics","Central Europe","Baltics & Poland"]:
    for yr in ["2024","2025"]:
        s=e[(e.bu==bu)&(e.year==yr)]
        rep=s.ebitda.sum(); oi=s.other_income.sum()
        if yr=="2024": r24=rep; u24=rep-oi
        else: r25=rep; u25=rep-oi
    print(f"{bu:18s} reported {r24:>12,.0f} -> {r25:>12,.0f} ({(r25/r24-1)*100:+6.1f}%)  "
          f"underlying {u24:>12,.0f} -> {u25:>12,.0f} ({(u25/u24-1)*100:+6.1f}%)")
# company
for yr in ["2024","2025"]:
    s=e[e.year==yr];
    if yr=="2024": cr24=s.ebitda.sum(); cu24=s.ebitda.sum()-s.other_income.sum()
    else: cr25=s.ebitda.sum(); cu25=s.ebitda.sum()-s.other_income.sum()
print(f"{'Company':18s} reported {cr24:>12,.0f} -> {cr25:>12,.0f} ({(cr25/cr24-1)*100:+6.1f}%)  "
      f"underlying {cu24:>12,.0f} -> {cu25:>12,.0f} ({(cu25/cu24-1)*100:+6.1f}%)")

print("\n=== Company gross margin foregone ===")
g=pnl.groupby(pnl.month.str[:4]).agg(net=("net_revenue","sum"),gp=("gross_profit","sum"))
gm24=g.loc["2024","gp"]/g.loc["2024","net"]; gm25=g.loc["2025","gp"]/g.loc["2025","net"]
print(f"GM 2024 {gm24*100:.2f}%  2025 {gm25*100:.2f}%  delta {(gm25-gm24)*100:+.2f}pp")
print(f"GP at 2024 margin on 2025 net: {gm24*g.loc['2025','net']:,.0f}  actual GP {g.loc['2025','gp']:,.0f}  foregone {gm24*g.loc['2025','net']-g.loc['2025','gp']:,.0f}")
print(f"GP YoY: {g.loc['2024','gp']:,.0f} -> {g.loc['2025','gp']:,.0f} ({(g.loc['2025','gp']/g.loc['2024','gp']-1)*100:+.1f}%) on net rev +{(g.loc['2025','net']/g.loc['2024','net']-1)*100:.1f}%")

print("\n=== Cash conversion 2024 vs 2025 ===")
for yr in ["2024","2025"]:
    ocf=cash[cash.month.str[:4]==yr].operating_cash_flow.sum()
    icf=cash[cash.month.str[:4]==yr].investing_cash_flow.sum()
    eb=e[e.year==yr].ebitda.sum(); ug=eb-e[e.year==yr].other_income.sum()
    print(f"{yr}: OCF {ocf:>12,.0f}  ICF {icf:>12,.0f}  reportedEBITDA {eb:>12,.0f}  OCF/underlyingEBITDA {ocf/ug*100:5.1f}%")
