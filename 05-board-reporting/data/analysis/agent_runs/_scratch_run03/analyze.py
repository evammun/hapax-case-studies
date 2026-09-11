import pandas as pd, numpy as np
pd.set_option('display.width',220); pd.set_option('display.max_columns',40); pd.set_option('display.max_rows',120)
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')

D='C:/Users/luigi/Dropbox/Archivio famiglia/Hapax/Case Studies/05 Board Reporting/data/'
pnl=pd.read_csv(D+'pnl_monthly.csv'); bud=pd.read_csv(D+'budget_pnl_monthly.csv')
opex=pd.read_csv(D+'opex_monthly.csv'); bopex=pd.read_csv(D+'budget_opex_monthly.csv')
cm=pd.read_csv(D+'customer_master.csv')
crev=pd.read_csv(D+'customer_revenue_monthly.csv')
wc=pd.read_csv(D+'working_capital_monthly.csv')
rbc=pd.read_csv(D+'receivables_by_customer_monthly.csv')
cash=pd.read_csv(D+'cash_monthly.csv')

def bu_pnl(df):
    g=df.groupby(['month','bu']).agg(vol=('volume_units','sum'),gross=('gross_revenue','sum'),
        disc=('promo_discounts','sum'),net=('net_revenue','sum'),mat=('material_cost','sum'),
        lab=('direct_labour','sum'),logi=('logistics_cost','sum'),gp=('gross_profit','sum')).reset_index()
    return g

def co_pnl(df):
    g=df.groupby(['month']).agg(vol=('volume_units','sum'),gross=('gross_revenue','sum'),
        disc=('promo_discounts','sum'),net=('net_revenue','sum'),mat=('material_cost','sum'),
        gp=('gross_profit','sum')).reset_index()
    return g

# ---------- CLUSTER 1: seasonality of Jan drop ----------
print('='*70); print('CLUSTER 1  company net revenue by month, actual vs budget')
a=co_pnl(pnl)[['month','net','vol']]; b=co_pnl(bud)[['month','net']].rename(columns={'net':'bnet'})
m=a.merge(b,on='month')
m['MoM_%']=m['net'].pct_change()*100
m['vs_bud_%']=(m['net']/m['bnet']-1)*100
# YoY
m['yoy_%']=m['net'].pct_change(12)*100
print(m.to_string(index=False))
