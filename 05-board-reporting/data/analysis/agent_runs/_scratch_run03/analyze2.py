import pandas as pd, numpy as np
pd.set_option('display.width',240); pd.set_option('display.max_columns',40); pd.set_option('display.max_rows',200)
pd.set_option('display.float_format', lambda x: f'{x:,.3f}')
D='C:/Users/luigi/Dropbox/Archivio famiglia/Hapax/Case Studies/05 Board Reporting/data/'
pnl=pd.read_csv(D+'pnl_monthly.csv'); bud=pd.read_csv(D+'budget_pnl_monthly.csv')

def add(df):
    df=df.copy()
    return df
# ---- Nordics per-unit economics actual vs budget, by month (aggregate over lines) ----
def buagg(df,bu):
    g=df[df.bu==bu].groupby('month').agg(vol=('volume_units','sum'),gross=('gross_revenue','sum'),
        disc=('promo_discounts','sum'),net=('net_revenue','sum'),mat=('material_cost','sum'),
        lab=('direct_labour','sum'),logi=('logistics_cost','sum'),gp=('gross_profit','sum')).reset_index()
    g['net_per_u']=g.net/g.vol; g['mat_per_u']=g.mat/g.vol; g['gross_per_u']=g.gross/g.vol
    g['disc_pct']=g.disc/g.gross*100; g['gm_pct']=g.gp/g.net*100; g['mat_pct_net']=g.mat/g.net*100
    return g

for BU in ['Nordics']:
    print('='*80); print('CLUSTER 2 -', BU, 'actual vs budget per-unit economics')
    a=buagg(pnl,BU); b=buagg(bud,BU)
    j=a.merge(b,on='month',suffixes=('','_b'))
    j['mat_perU_YoY%']=j.mat_per_u.pct_change(12)*100
    j['net_perU_YoY%']=j.net_per_u.pct_change(12)*100
    j['vol_YoY%']=j.vol.pct_change(12)*100
    cols=['month','vol','vol_YoY%','net_per_u','net_perU_YoY%','mat_per_u','mat_perU_YoY%',
          'mat_per_u_b','disc_pct','disc_pct_b','gm_pct','gm_pct_b','mat_pct_net','mat_pct_net_b']
    print(j[cols].to_string(index=False))

# ---- Nordics by line: is margin compression a mix shift or within-line? ----
print('='*80); print('CLUSTER 2 - Nordics FY2024 vs FY2025 by line: volume share, net/u, mat/u, GM%')
def lineagg(df,year):
    d=df[(df.bu=='Nordics')&(df.month.str[:4]==year)]
    g=d.groupby('line').agg(vol=('volume_units','sum'),net=('net_revenue','sum'),
        gross=('gross_revenue','sum'),disc=('promo_discounts','sum'),
        mat=('material_cost','sum'),gp=('gross_profit','sum')).reset_index()
    g['net_per_u']=g.net/g.vol; g['mat_per_u']=g.mat/g.vol; g['gm_pct']=g.gp/g.net*100
    g['disc_pct']=g.disc/g.gross*100
    g['vol_share']=g.vol/g.vol.sum()*100
    g['year']=year
    return g
for y in ['2024','2025']:
    print('-- Nordics',y,'--')
    print(lineagg(pnl,y)[['line','year','vol','vol_share','net_per_u','disc_pct','mat_per_u','gm_pct']].to_string(index=False))

# list price actual vs budget by line Nordics (avg over year)
print('='*80); print('Nordics list_price actual vs budget by line (FY2025 avg, volume-wtd)')
def lp(df,year):
    d=df[(df.bu=='Nordics')&(df.month.str[:4]==year)].copy()
    d['lp_x_v']=d.list_price_eur*d.volume_units
    g=d.groupby('line').apply(lambda x: pd.Series({'wlp':x.lp_x_v.sum()/x.volume_units.sum()})).reset_index()
    return g
la=lp(pnl,'2025').rename(columns={'wlp':'act_lp'}); lb=lp(bud,'2025').rename(columns={'wlp':'bud_lp'})
print(la.merge(lb,on='line').assign(diff_pct=lambda x:(x.act_lp/x.bud_lp-1)*100).to_string(index=False))
