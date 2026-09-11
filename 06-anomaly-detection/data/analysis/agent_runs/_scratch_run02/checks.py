import pandas as pd, json, numpy as np, re
from pathlib import Path
BASE = Path(r"C:\Users\luigi\Dropbox\Archivio famiglia\Hapax\Case Studies\06 Anomaly Detection")
D = BASE / "data"
gl = pd.read_csv(D/"gl_transactions.csv", dtype={'account':str})
vm = pd.read_csv(D/"vendor_master.csv", dtype={'allowed_accounts':str})
cal = pd.read_csv(D/"company_calendar.csv")
rf = pd.read_csv(D/"analysis/rule_flags.csv")
det = pd.read_csv(D/"analysis/detector_flags.csv")
clusters = json.load(open(D/"analysis/clusters.json", encoding='utf-8'))
for c in ['posting_date','invoice_date','due_date']:
    gl[c] = pd.to_datetime(gl[c])
cal['date'] = pd.to_datetime(cal['date'])
wd = dict(zip(cal['date'], cal['is_working_day']))
gl['post_wd'] = gl['posting_date'].map(wd)
allowed = {r.vendor_id: set(str(r.allowed_accounts).split(';')) for r in vm.itertuples()}
gl['allowed'] = gl['vendor_id'].map(allowed)
gl['mapping_viol'] = gl.apply(lambda r: r['account'] not in r['allowed'] if isinstance(r['allowed'],set) else False, axis=1)

print("### 1. RULE CALIBRATION (ledger-wide vs flagged) ###")
# mapping violations ledger-wide
mv = gl[gl['mapping_viol']]
print(f"Mapping violations ledger-wide: {len(mv)} rows, vendors={mv['vendor_id'].unique().tolist()}")
# round sum exact thousands >=2000
rs = gl[(gl['amount_eur']>=2000) & (gl['amount_eur']%1000==0)]
print(f"Round-sum (exact k, >=2000) ledger-wide: {len(rs)} rows, vendors={sorted(rs['vendor_id'].unique().tolist())}")
print(rs.groupby('vendor_id')['amount_eur'].agg(['count','sum']).to_string())
# near threshold 9500-9999.99
nt = gl[(gl['amount_eur']>=9500)&(gl['amount_eur']<=9999.99)]
print(f"Near-threshold 9500-9999.99 ledger-wide: {len(nt)} rows, vendors={sorted(nt['vendor_id'].unique().tolist())}")
print(nt[['txn_id','vendor_id','amount_eur','account','posted_by']].to_string())

print("\n### 2. NON-WORKING-DAY HUMAN POSTINGS per user (full ledger) ###")
hum = gl[gl['posted_by']!='INTEG-01']
nwd = hum[hum['post_wd']==False]
print("human rows total by user:\n", hum['posted_by'].value_counts().to_string())
print("non-working-day human rows by user:\n", nwd['posted_by'].value_counts().to_string())
print("INTEG-01 non-working-day rows:", (gl[(gl['posted_by']=='INTEG-01') & (gl['post_wd']==False)]).shape[0])

print("\n### 3. DUPLICATE PAIRS ledger-wide (same vendor+exact amount, <=7 days, diff invoice) ###")
g = gl.sort_values('posting_date')
dups=[]
for (v,a),sub in g.groupby(['vendor_id','amount_eur']):
    if len(sub)>1:
        rows=sub.sort_values('posting_date').to_dict('records')
        for i in range(len(rows)-1):
            for j in range(i+1,len(rows)):
                gap=(rows[j]['posting_date']-rows[i]['posting_date']).days
                if 0<=gap<=7 and rows[i]['invoice_number']!=rows[j]['invoice_number']:
                    dups.append((v,a,rows[i]['txn_id'],rows[j]['txn_id'],gap,rows[i]['memo'],rows[j]['memo']))
print(f"total duplicate pairs ledger-wide: {len(dups)}")
for d in dups:
    print(d)

print("\n### 4. VENDOR MASTER HYGIENE ###")
# VAT collisions
vc = vm.groupby('vat_id')['vendor_id'].apply(list)
print("VAT ids on >1 vendor_id:")
for vat,ids in vc.items():
    if len(ids)>1:
        print(f"  VAT {vat}: {ids}  names={vm[vm.vendor_id.isin(ids)]['vendor_name'].tolist()}  ibans={vm[vm.vendor_id.isin(ids)]['iban'].tolist()}")
# IBAN collisions
ic = vm.groupby('iban')['vendor_id'].apply(list)
print("IBANs on >1 vendor_id:")
any_iban=False
for iban,ids in ic.items():
    if len(ids)>1:
        any_iban=True; print(f"  IBAN {iban}: {ids}")
if not any_iban: print("  none")
# normalized name collisions
def norm(n): return re.sub(r'[^a-z0-9]','',str(n).lower())
vm['nn']=vm['vendor_name'].map(norm)
ncoll=vm.groupby('nn')['vendor_id'].apply(list)
print("normalized-name collisions (>1 vendor_id):")
for nn,ids in ncoll.items():
    if len(ids)>1:
        print(f"  '{nn}': {ids} names={vm[vm.vendor_id.isin(ids)]['vendor_name'].tolist()}")
# shared address
ac=vm.groupby('address')['vendor_id'].apply(list)
print("shared addresses (>1 vendor_id):")
for ad,ids in ac.items():
    if len(ids)>1:
        print(f"  {ad}: {ids} names={vm[vm.vendor_id.isin(ids)]['vendor_name'].tolist()}")

print("\n### 5. postings before active_from ###")
vm2=vm.set_index('vendor_id'); vm['active_from']=pd.to_datetime(vm['active_from'])
af=dict(zip(vm['vendor_id'],vm['active_from']))
gl['af']=gl['vendor_id'].map(af)
early=gl[gl['invoice_date']<gl['af']]
print("invoices before vendor active_from:", len(early))

print("\n### 6. detector/singles/residual txns that ALSO carry a rule flag ###")
ruleset=set(rf['txn_id'])
detset=set(det['txn_id'])
print("overlap rule∩detector:", sorted(ruleset & detset))

print("\n### 7. spend by month/account, H1 vs H2 top movers ###")
gl['half']='H1'; gl.loc[gl['posting_date'].dt.month>=7,'half']='H2'
piv=gl.groupby(['vendor_id','half'])['amount_eur'].sum().unstack(fill_value=0)
piv['delta']=piv.get('H2',0)-piv.get('H1',0)
piv['name']=piv.index.map(dict(zip(vm['vendor_id'],vm['vendor_name'])))
print("Top 8 H2>H1 movers:\n", piv.sort_values('delta',ascending=False).head(8)[['H1','H2','delta','name']].to_string())
print("Top 8 H1>H2 movers:\n", piv.sort_values('delta').head(8)[['H1','H2','delta','name']].to_string())
# monthly account totals - biggest single month-account spikes vs median
gl['ym']=gl['posting_date'].dt.month
ma=gl.groupby(['account','ym'])['amount_eur'].sum().unstack(fill_value=0)
rel=ma.div(ma.median(axis=1),axis=0)
print("month-account cells > 2.2x that account's median month (potential spikes):")
for acc in rel.index:
    for m in rel.columns:
        if rel.loc[acc,m]>2.2 and ma.loc[acc,m]>50000:
            print(f"  acct {acc} month {m}: {ma.loc[acc,m]:.0f} ({rel.loc[acc,m]:.1f}x median)")
