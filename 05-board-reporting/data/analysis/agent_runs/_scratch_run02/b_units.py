import pandas as pd
from pathlib import Path
D = Path(r"C:\Users\luigi\Dropbox\Archivio famiglia\Hapax\Case Studies\05 Board Reporting\data")
pd.set_option("display.width", 240, "display.max_columns", 40, "display.max_rows", 300)
pnl = pd.read_csv(D/"pnl_monthly.csv"); pnl["year"]=pnl["month"].str[:4]

# discount rate by BU by month
g = pnl.groupby(["month","bu"],as_index=False).agg(gross=("gross_revenue","sum"),
    promo=("promo_discounts","sum"), net=("net_revenue","sum"), mat=("material_cost","sum"),
    gp=("gross_profit","sum"), vol=("volume_units","sum"))
g["disc_rate"]=g["promo"]/g["gross"]; g["gm"]=g["gp"]/g["net"]
print("=== DISCOUNT RATE by BU by month (pivot) ===")
print(g.pivot(index="month",columns="bu",values="disc_rate").round(4).to_string())
print("\n=== GROSS MARGIN % by BU by month ===")
print(g.pivot(index="month",columns="bu",values="gm").round(4).to_string())

# Unit economics by BU by year
u = pnl.groupby(["year","bu"],as_index=False).agg(vol=("volume_units","sum"),
    gross=("gross_revenue","sum"), promo=("promo_discounts","sum"), net=("net_revenue","sum"),
    mat=("material_cost","sum"), lab=("direct_labour","sum"), log=("logistics_cost","sum"), gp=("gross_profit","sum"))
u["net_per_u"]=u["net"]/u["vol"]; u["mat_per_u"]=u["mat"]/u["vol"]
u["gross_per_u"]=u["gross"]/u["vol"]; u["disc_rate"]=u["promo"]/u["gross"]; u["gm"]=u["gp"]/u["net"]
print("\n=== UNIT ECONOMICS by BU by YEAR ===")
print(u[["year","bu","vol","gross_per_u","net_per_u","mat_per_u","disc_rate","gm"]].round(4).to_string(index=False))

# By line by year, company
ul = pnl.groupby(["year","line"],as_index=False).agg(vol=("volume_units","sum"),
    gross=("gross_revenue","sum"), promo=("promo_discounts","sum"), net=("net_revenue","sum"),
    mat=("material_cost","sum"), gp=("gross_profit","sum"))
ul["net_per_u"]=ul["net"]/ul["vol"]; ul["mat_per_u"]=ul["mat"]/ul["vol"]
ul["disc_rate"]=ul["promo"]/ul["gross"]; ul["gm"]=ul["gp"]/ul["net"]; ul["volshare"]=ul["vol"]/ul.groupby("year")["vol"].transform("sum")
print("\n=== BY PRODUCT LINE by YEAR (company) ===")
print(ul[["year","line","vol","volshare","net_per_u","mat_per_u","disc_rate","gm"]].round(4).to_string(index=False))
