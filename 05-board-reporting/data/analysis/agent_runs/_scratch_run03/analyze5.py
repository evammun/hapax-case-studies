import pandas as pd, numpy as np
pd.set_option('display.width',220); pd.set_option('display.max_columns',40); pd.set_option('display.max_rows',60)
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')
D='C:/Users/luigi/Dropbox/Archivio famiglia/Hapax/Case Studies/05 Board Reporting/data/'
pnl=pd.read_csv(D+'pnl_monthly.csv')
opex=pd.read_csv(D+'opex_monthly.csv')
crev=pd.read_csv(D+'customer_revenue_monthly.csv')
rbc=pd.read_csv(D+'receivables_by_customer_monthly.csv')

# Rheinkauf monthly: revenue vs collections vs AR
print('Rheinkauf Gruppe monthly (net rev, collections, closing AR, AR/mo-rev)')
r_rev=crev[(crev.customer=='Rheinkauf Gruppe')].set_index('month').net_revenue
r_ar =rbc[(rbc.customer=='Rheinkauf Gruppe')].set_index('month')[['receivables_closing','collections']]
z=pd.concat([r_rev.rename('netrev'),r_ar],axis=1)
z['AR_over_morev']=z.receivables_closing/z.netrev
print(z.loc['2024-06':'2025-12'].to_string())

# CE AR build share from Rheinkauf
ce=rbc[rbc.bu=='Central Europe']
ce_ar=ce.groupby('month').receivables_closing.sum()
rh_ar=rbc[rbc.customer=='Rheinkauf Gruppe'].groupby('month').receivables_closing.sum()
print('\nCE total AR Dec24->Dec25 build: %.0f ; Rheinkauf build: %.0f ; share %.1f%%'%(
    ce_ar['2025-12']-ce_ar['2024-12'], rh_ar['2025-12']-rh_ar['2024-12'],
    (rh_ar['2025-12']-rh_ar['2024-12'])/(ce_ar['2025-12']-ce_ar['2024-12'])*100))
print('Rheinkauf net rev YoY (FY24->FY25): %.0f -> %.0f (%.1f%%)'%(
    crev[(crev.customer=='Rheinkauf Gruppe')&(crev.month.str[:4]=='2024')].net_revenue.sum(),
    crev[(crev.customer=='Rheinkauf Gruppe')&(crev.month.str[:4]=='2025')].net_revenue.sum(),
    (crev[(crev.customer=='Rheinkauf Gruppe')&(crev.month.str[:4]=='2025')].net_revenue.sum()/
     crev[(crev.customer=='Rheinkauf Gruppe')&(crev.month.str[:4]=='2024')].net_revenue.sum()-1)*100))

# Company discount % trend
print('\nCompany gross->net discount % by month')
g=pnl.groupby('month').agg(gross=('gross_revenue','sum'),disc=('promo_discounts','sum'),net=('net_revenue','sum'),gp=('gross_profit','sum'))
g['disc_pct']=g.disc/g.gross*100; g['gm_pct']=g.gp/g.net*100
print(g[['disc_pct','gm_pct']].to_string())

# FY EBITDA reported vs underlying both years, gross margin, ebitda margin
print('\nFY reported vs underlying EBITDA')
for y in ['2024','2025']:
    p=pnl[pnl.month.str[:4]==y]; o=opex[opex.month.str[:4]==y]
    net=p.net_revenue.sum(); gp=p.gross_profit.sum()
    sm=o.sales_marketing.sum(); ad=o.admin_general.sum(); oi=o.other_income.sum()
    rep=gp-sm-ad+oi; und=gp-sm-ad
    print('%s net=%.0f gm%%=%.1f rep_EBITDA=%.0f (%.1f%%) und_EBITDA=%.0f (%.1f%%) other_inc=%.0f'%(
        y,net,gp/net*100,rep,rep/net*100,und,und/net*100,oi))
