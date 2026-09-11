import pandas as pd, numpy as np
pd.set_option('display.width',250); pd.set_option('display.max_columns',40); pd.set_option('display.max_rows',400)
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')
D='C:/Users/luigi/Dropbox/Archivio famiglia/Hapax/Case Studies/05 Board Reporting/data/'
pnl=pd.read_csv(D+'pnl_monthly.csv')
opex=pd.read_csv(D+'opex_monthly.csv'); bopex=pd.read_csv(D+'budget_opex_monthly.csv')
crev=pd.read_csv(D+'customer_revenue_monthly.csv'); cm=pd.read_csv(D+'customer_master.csv')
wc=pd.read_csv(D+'working_capital_monthly.csv'); rbc=pd.read_csv(D+'receivables_by_customer_monthly.csv')
cash=pd.read_csv(D+'cash_monthly.csv')

# ---------- CLUSTER 5: Central Europe DSO by customer ----------
print('='*80); print('CLUSTER 5 - Central Europe receivables_closing by customer (selected months)')
ce=rbc[rbc.bu=='Central Europe'].copy()
piv=ce.pivot_table(index='customer',columns='month',values='receivables_closing',aggfunc='sum')
sel=['2024-06','2024-12','2025-01','2025-04','2025-06','2025-09','2025-12']
piv=piv[sel]
piv['chg_24_12_to_25_12']=piv['2025-12']-piv['2024-12']
print(piv.sort_values('chg_24_12_to_25_12',ascending=False).to_string())

# implied DSO per customer: closing AR / (that customer's trailing-3m avg daily net revenue)
print('-- CE per-customer: closing AR Dec25 vs avg monthly net rev H2-25, ratio (months of revenue in AR)')
cer=crev[crev.bu=='Central Europe'].copy()
rev25=cer[(cer.month>='2025-07')&(cer.month<='2025-12')].groupby('customer').net_revenue.mean()
ar_dec=ce[ce.month=='2025-12'].set_index('customer').receivables_closing
coll_dec=ce[ce.month=='2025-12'].set_index('customer').collections
t=pd.concat([ar_dec.rename('AR_Dec25'),rev25.rename('avg_mo_netrev_H2'),coll_dec.rename('coll_Dec25')],axis=1)
t['AR_months_of_rev']=t.AR_Dec25/t.avg_mo_netrev_H2
t=t.merge(cm[['customer','contractual_terms_days','channel']],left_index=True,right_on='customer')
print(t.sort_values('AR_Dec25',ascending=False).to_string(index=False))

# CE collections vs revenue trend: are collections lagging?
print('-- CE monthly: net rev, collections, closing AR, closing/opening')
cewc=wc[wc.bu=='Central Europe'].copy()
cerev=cer.groupby('month').net_revenue.sum().rename('netrev')
z=cewc.merge(cerev,on='month')
z['coll_over_rev']=z.collections/z.netrev
print(z[['month','netrev','receivables_opening','collections','receivables_closing','coll_over_rev']].to_string(index=False))

# ---------- CLUSTER 6: April other income + investing CF ----------
print('='*80); print('CLUSTER 6 - other_income by BU by month (non-zero only) + cash investing CF')
oi=opex[opex.other_income!=0][['month','bu','other_income']]
print(oi.to_string(index=False))
print('-- cash_monthly full:')
print(cash.to_string(index=False))

# ---------- Cross-cut: company operating cash flow vs reported EBITDA (working capital) ----------
print('='*80); print('MISSED? Operating cash flow vs reported EBITDA (company), and total receivables build')
gp=pnl.groupby('month').gross_profit.sum()
ox=opex.groupby('month').agg(sm=('sales_marketing','sum'),ad=('admin_general','sum'),oi=('other_income','sum'))
eb=(gp-ox.sm-ox.ad+ox.oi).rename('rep_ebitda')
ebu=(gp-ox.sm-ox.ad).rename('und_ebitda')
arc=wc.groupby('month').receivables_closing.sum().rename('AR_close')
c=cash.set_index('month')
tt=pd.concat([eb,ebu,c.operating_cash_flow,c.investing_cash_flow,arc],axis=1)
tt['AR_build_MoM']=tt.AR_close.diff()
print(tt.loc['2025-01':'2025-12'].to_string())
print('FY2025 sums: rep_ebitda=%.0f und_ebitda=%.0f op_CF=%.0f inv_CF=%.0f AR_build(Dec24->Dec25)=%.0f'%(
    tt.loc['2025-01':'2025-12'].rep_ebitda.sum(), tt.loc['2025-01':'2025-12'].und_ebitda.sum(),
    tt.loc['2025-01':'2025-12'].operating_cash_flow.sum(), tt.loc['2025-01':'2025-12'].investing_cash_flow.sum(),
    arc['2025-12']-arc['2024-12']))
