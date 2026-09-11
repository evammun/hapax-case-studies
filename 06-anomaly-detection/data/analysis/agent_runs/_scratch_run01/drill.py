import json
from pathlib import Path
import pandas as pd, numpy as np
pd.set_option('display.max_columns',None); pd.set_option('display.width',260); pd.set_option('display.max_colwidth',60)
BASE=Path(r"C:\Users\luigi\Dropbox\Archivio famiglia\Hapax\Case Studies\06 Anomaly Detection"); D=BASE/"data"; A=D/"analysis"
gl=pd.read_csv(D/"gl_transactions.csv",dtype={'invoice_number':str})
vm=pd.read_csv(D/"vendor_master.csv",dtype=str)
df_=pd.read_csv(A/"detector_flags.csv"); rf=pd.read_csv(A/"rule_flags.csv")
clusters=json.loads((A/"clusters.json").read_text(encoding="utf-8"))
for c in ['posting_date','invoice_date','due_date']: gl[c]=pd.to_datetime(gl[c])
gl['account']=gl['account'].astype(str)
vinfo=vm.set_index('vendor_id')
flagged=set(df_['txn_id'])|set(rf['txn_id'])

print("== Largest transactions in whole ledger (top 15) ==")
top=gl.nlargest(15,'amount_eur')[['txn_id','posting_date','vendor_id','vendor_name','account','amount_eur','posted_by','memo']]
top['ruleflag']=top['txn_id'].isin(set(rf['txn_id'])); top['detflag']=top['txn_id'].isin(set(df_['txn_id']))
print(top.to_string(index=False))

print("\n== V-0019 Konepaja Ristimaki (the 78,400 vendor) all txns ==")
print(gl[gl['vendor_id']=='V-0019'][['txn_id','posting_date','account','amount_eur','invoice_number','posted_by','memo']].to_string(index=False))

print("\n== U-058 top postings ==")
print(gl[gl['posted_by']=='U-058'].nlargest(6,'amount_eur')[['txn_id','posting_date','vendor_id','vendor_name','account','amount_eur','memo']].to_string(index=False))
print("\n== U-204 top postings ==")
print(gl[gl['posted_by']=='U-204'].nlargest(6,'amount_eur')[['txn_id','posting_date','vendor_id','vendor_name','account','amount_eur','memo']].to_string(index=False))

print("\n== Karrenbach three vendors - full txn detail (check duplicate amounts across ids) ==")
k=gl[gl['vendor_id'].isin(['V-0003','V-0004','V-0005'])].sort_values(['amount_eur'])
print(k[['txn_id','posting_date','vendor_id','account','amount_eur','invoice_number','posted_by','memo']].to_string(index=False))
# any identical amounts across the 3 ids?
dup_amounts=k['amount_eur'].value_counts()
print("amounts appearing >1x across the 3 Karrenbach ids:", dup_amounts[dup_amounts>1].to_dict())

print("\n== Detector-vendor units: share of flags on vendor's MINORITY allowed account & amount percentile ==")
allowed=vm.set_index('vendor_id')['allowed_accounts'].apply(lambda s:str(s).split(';')).to_dict()
for u in clusters:
    if u['unit_type']=='detector_vendor':
        vid=u['group_key']; vs=gl[gl['vendor_id']==vid]
        prim=vs['account'].value_counts().idxmax()
        ids=u['txn_ids']; fsub=gl[gl['txn_id'].isin(ids)]
        n_minor=(fsub['account']!=prim).sum()
        # amount percentile of each flagged txn within vendor dist
        pcts=[ (vs['amount_eur']<a).mean() for a in fsub['amount_eur'] ]
        hi=sum(1 for p in pcts if p>=0.80)
        print(f"{u['unit_id']} {vid}: nflag={len(ids)} on_minority_acct={n_minor} amt>=80thpctile={hi} primary_acct={prim}({(vs['account']==prim).mean():.0%})")

print("\n== RESIDUAL quick profile ==")
res=[u for u in clusters if u['unit_id']=='RESIDUAL'][0]['txn_ids']
r=gl[gl['txn_id'].isin(res)]
r=r.assign(minor=[a not in allowed[v][:1] for a,v in zip(r['account'],r['vendor_id'])])
print(f"n={len(r)} total={r['amount_eur'].sum():.2f} amt range {r['amount_eur'].min():.2f}-{r['amount_eur'].max():.2f} mean {r['amount_eur'].mean():.2f}")
print("on non-allowed account:", sum(1 for a,v in zip(r['account'],r['vendor_id']) if a not in allowed[v]))
print("posters:", r['posted_by'].value_counts().to_dict())
print("any rule-flagged in residual:", r['txn_id'].isin(set(rf['txn_id'])).sum())
# residual amount vs each vendor's own max
overmax=0
for _,row in r.iterrows():
    vs=gl[gl['vendor_id']==row['vendor_id']]
    if row['amount_eur']>=vs['amount_eur'].quantile(0.9): overmax+=1
print("residual txns in top-10% of their vendor's amounts:", overmax, "of", len(r))
