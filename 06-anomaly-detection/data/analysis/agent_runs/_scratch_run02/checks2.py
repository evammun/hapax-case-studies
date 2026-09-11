import pandas as pd, json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
BASE = Path(r"C:\Users\luigi\Dropbox\Archivio famiglia\Hapax\Case Studies\06 Anomaly Detection")
D = BASE / "data"
gl = pd.read_csv(D/"gl_transactions.csv", dtype={'account':str})
vm = pd.read_csv(D/"vendor_master.csv", dtype={'allowed_accounts':str})
rf = pd.read_csv(D/"analysis/rule_flags.csv")
det = pd.read_csv(D/"analysis/detector_flags.csv")
for c in ['posting_date','invoice_date','due_date']:
    gl[c]=pd.to_datetime(gl[c])

print("### 6. overlap rule ∩ detector ###")
print(sorted(set(rf['txn_id']) & set(det['txn_id'])))

print("\n### Kärrenbach triple identity V-0003/4/5 transactions ###")
k = gl[gl['vendor_id'].isin(['V-0003','V-0004','V-0005'])]
print("counts by vendor_id:\n", k.groupby('vendor_id').agg(n=('amount_eur','size'), total=('amount_eur','sum'), first=('posting_date','min'), last=('posting_date','max')).to_string())
print("account used:", k['account'].value_counts().to_dict())
# same-amount cross-id pairs (possible double pay across the 3 ids)
print("cross-id same-amount within 10 days:")
kk=k.sort_values('posting_date').to_dict('records')
found=False
for i in range(len(kk)):
    for j in range(i+1,len(kk)):
        if kk[i]['vendor_id']!=kk[j]['vendor_id'] and abs(kk[i]['amount_eur']-kk[j]['amount_eur'])<0.01:
            gap=abs((kk[j]['posting_date']-kk[i]['posting_date']).days)
            if gap<=15:
                found=True; print("  ",kk[i]['vendor_id'],kk[i]['txn_id'],kk[i]['amount_eur'],kk[i]['posting_date'].date(),"<->",kk[j]['vendor_id'],kk[j]['txn_id'],kk[j]['posting_date'].date(),"gap",gap)
if not found: print("  none within 15 days")
print("monthly spend V-0003/4/5 (each id, by month):")
k['m']=k['posting_date'].dt.month
print(k.pivot_table(index='m',columns='vendor_id',values='amount_eur',aggfunc='sum',fill_value=0).to_string())

print("\n### 7b. H1 vs H2 movers & monthly account spikes ###")
gl['half']=['H2' if m>=7 else 'H1' for m in gl['posting_date'].dt.month]
piv=gl.groupby(['vendor_id','half'])['amount_eur'].sum().unstack(fill_value=0)
for h in ['H1','H2']:
    if h not in piv: piv[h]=0
piv['delta']=piv['H2']-piv['H1']
piv['name']=piv.index.map(dict(zip(vm['vendor_id'],vm['vendor_name'])))
print("Top 6 H2>H1:\n", piv.sort_values('delta',ascending=False).head(6)[['H1','H2','delta','name']].to_string())
print("Top 6 H1>H2:\n", piv.sort_values('delta').head(6)[['H1','H2','delta','name']].to_string())
gl['ym']=gl['posting_date'].dt.month
ma=gl.groupby(['account','ym'])['amount_eur'].sum().unstack(fill_value=0)
rel=ma.div(ma.median(axis=1),axis=0)
print("month-account spikes >2.2x median & >50k:")
hits=False
for acc in rel.index:
    for m in rel.columns:
        if rel.loc[acc,m]>2.2 and ma.loc[acc,m]>50000:
            hits=True; print(f"  acct {acc} month {m}: {ma.loc[acc,m]:.0f} ({rel.loc[acc,m]:.1f}x)")
if not hits: print("  none")

# detector-vendor units: any account outside allowed among their txns?
print("\n### detector units: account-outside-allowed check among all detector txns ###")
allowed={r.vendor_id:set(str(r.allowed_accounts).split(';')) for r in vm.itertuples()}
dd=gl[gl['txn_id'].isin(set(det['txn_id']))].copy()
dd['viol']=dd.apply(lambda r: r['account'] not in allowed.get(r['vendor_id'],set()), axis=1)
print("detector txns with mapping violation:", dd['viol'].sum())
# detector txns >=10000 or >=9500
print("detector txns >=9500:", dd[dd['amount_eur']>=9500][['txn_id','vendor_id','amount_eur','account']].to_string())
print("detector txns that are exact round thousands >=2000:", dd[(dd['amount_eur']>=2000)&(dd['amount_eur']%1000==0)]['txn_id'].tolist())
