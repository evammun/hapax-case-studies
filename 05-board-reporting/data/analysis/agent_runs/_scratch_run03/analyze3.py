import pandas as pd, numpy as np
pd.set_option('display.width',240); pd.set_option('display.max_columns',40); pd.set_option('display.max_rows',300)
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')
D='C:/Users/luigi/Dropbox/Archivio famiglia/Hapax/Case Studies/05 Board Reporting/data/'
pnl=pd.read_csv(D+'pnl_monthly.csv'); bud=pd.read_csv(D+'budget_pnl_monthly.csv')
opex=pd.read_csv(D+'opex_monthly.csv'); bopex=pd.read_csv(D+'budget_opex_monthly.csv')
crev=pd.read_csv(D+'customer_revenue_monthly.csv'); cm=pd.read_csv(D+'customer_master.csv')

# ---------- CLUSTER 3: Baltics & Poland growth + margin ----------
print('='*80); print('CLUSTER 3 - Baltics & Poland: by line FY24 vs FY25')
def lineagg(df,year,bu):
    d=df[(df.bu==bu)&(df.month.str[:4]==year)]
    g=d.groupby('line').agg(vol=('volume_units','sum'),net=('net_revenue','sum'),
        gross=('gross_revenue','sum'),disc=('promo_discounts','sum'),
        mat=('material_cost','sum'),gp=('gross_profit','sum')).reset_index()
    g['net_per_u']=g.net/g.vol; g['mat_per_u']=g.mat/g.vol; g['gm_pct']=g.gp/g.net*100
    g['disc_pct']=g.disc/g.gross*100; g['vol_share']=g.vol/g.vol.sum()*100; g['year']=year
    return g
for y in ['2024','2025']:
    print('--',y);print(lineagg(pnl,y,'Baltics & Poland')[['line','vol','vol_share','net_per_u','disc_pct','mat_per_u','gm_pct']].to_string(index=False))

print('-- B&P monthly gm%, disc%, vol YoY, net & mat totals YoY, vs budget net')
def buagg(df,bu):
    g=df[df.bu==bu].groupby('month').agg(vol=('volume_units','sum'),gross=('gross_revenue','sum'),
        disc=('promo_discounts','sum'),net=('net_revenue','sum'),mat=('material_cost','sum'),gp=('gross_profit','sum')).reset_index()
    g['gm_pct']=g.gp/g.net*100; g['disc_pct']=g.disc/g.gross*100; g['mat_per_u']=g.mat/g.vol
    return g
a=buagg(pnl,'Baltics & Poland'); a['vol_YoY%']=a.vol.pct_change(12)*100; a['gm_YoY_pp']=a.gm_pct-a.gm_pct.shift(12)
print(a[a.month.str[:4]=='2025'][['month','vol','vol_YoY%','disc_pct','mat_per_u','gm_pct','gm_YoY_pp']].to_string(index=False))

# B&P customer concentration: who is growing
print('-- B&P net revenue by customer: 2024 H2 avg vs 2025 H2 avg (monthly)')
bp=crev[crev.bu=='Baltics & Poland'].copy()
for per,lab in [(['2024-07','2024-12'],'24H2'),(['2025-07','2025-12'],'25H2')]:
    pass
g24=bp[(bp.month>='2024-01')&(bp.month<='2024-12')].groupby('customer').net_revenue.sum()
g25=bp[(bp.month>='2025-01')&(bp.month<='2025-12')].groupby('customer').net_revenue.sum()
t=pd.concat([g24.rename('FY24'),g25.rename('FY25')],axis=1); t['growth']=t.FY25-t.FY24; t['g%']=(t.FY25/t.FY24-1)*100
print(t.sort_values('growth',ascending=False).to_string())

# ---------- CLUSTER 4: EBITDA vs budget bridge by BU ----------
print('='*80); print('CLUSTER 4 - EBITDA vs budget bridge by BU (FY2025 sum): GP var, S&M var, admin var, other_inc var')
def ebitda_tbl(pnl,opex):
    gp=pnl.groupby(['month','bu']).gross_profit.sum().reset_index()
    ox=opex.groupby(['month','bu']).agg(sm=('sales_marketing','sum'),ad=('admin_general','sum'),oi=('other_income','sum')).reset_index()
    m=gp.merge(ox,on=['month','bu'])
    m['ebitda']=m.gross_profit-m.sm-m.ad+m.oi
    return m
A=ebitda_tbl(pnl,opex); B=ebitda_tbl(bud,bopex)
j=A.merge(B,on=['month','bu'],suffixes=('','_b'))
fy=j[j.month.str[:4]=='2025'].groupby('bu').agg(gp=('gross_profit','sum'),gp_b=('gross_profit_b','sum'),
    sm=('sm','sum'),sm_b=('sm_b','sum'),ad=('ad','sum'),ad_b=('ad_b','sum'),
    oi=('oi','sum'),oi_b=('oi_b','sum'),eb=('ebitda','sum'),eb_b=('ebitda_b','sum')).reset_index()
fy['GP_var']=fy.gp-fy.gp_b; fy['SM_var']=-(fy.sm-fy.sm_b); fy['AD_var']=-(fy.ad-fy.ad_b); fy['OI_var']=fy.oi-fy.oi_b
fy['EBITDA_var']=fy.eb-fy.eb_b
print(fy[['bu','eb','eb_b','EBITDA_var','GP_var','SM_var','AD_var','OI_var']].to_string(index=False))
print('check EBITDA_var == GP+SM+AD+OI:', np.allclose(fy.EBITDA_var, fy.GP_var+fy.SM_var+fy.AD_var+fy.OI_var))
print('-- opex actual vs budget FY2025 by BU (S&M, admin) and as % of net rev')
netbu=pnl[pnl.month.str[:4]=='2025'].groupby('bu').net_revenue.sum()
print('S&M actual/bud, admin actual/bud:')
print(fy[['bu','sm','sm_b','ad','ad_b']].to_string(index=False))
