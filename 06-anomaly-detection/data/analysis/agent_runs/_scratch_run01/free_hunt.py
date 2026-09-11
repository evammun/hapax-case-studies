import json
from pathlib import Path
import pandas as pd, numpy as np
pd.set_option('display.max_columns',None); pd.set_option('display.width',260); pd.set_option('display.max_colwidth',50)
BASE=Path(r"C:\Users\luigi\Dropbox\Archivio famiglia\Hapax\Case Studies\06 Anomaly Detection"); D=BASE/"data"; A=D/"analysis"
gl=pd.read_csv(D/"gl_transactions.csv",dtype={'invoice_number':str})
vm=pd.read_csv(D/"vendor_master.csv",dtype=str)
df_=pd.read_csv(A/"detector_flags.csv"); rf=pd.read_csv(A/"rule_flags.csv")
for c in ['posting_date','invoice_date','due_date']: gl[c]=pd.to_datetime(gl[c])
gl['account']=gl['account'].astype(str); gl['pmonth']=gl['posting_date'].dt.month
gl['half']=np.where(gl['pmonth']<=6,'H1','H2')
vinfo=vm.set_index('vendor_id')
score_map=dict(zip(df_['txn_id'],df_['anomaly_score']))
flagged_ids=set(df_['txn_id'])

print("###### 1. VENDOR MASTER HYGIENE ######")
print("\n-- shared VAT across vendor_ids --")
for vat,g in vm.groupby('vat_id'):
    if len(g)>1:
        print(f"VAT {vat}: {list(zip(g['vendor_id'],g['vendor_name'],g['iban']))}")
print("\n-- shared IBAN across vendor_ids --")
for ib,g in vm.groupby('iban'):
    if len(g)>1:
        print(f"IBAN {ib}: {list(zip(g['vendor_id'],g['vendor_name']))}")
print("\n-- normalised-name collisions (case/space-insensitive) --")
vm['nname']=vm['vendor_name'].str.upper().str.replace(' ','',regex=False)
for nn,g in vm.groupby('nname'):
    if len(g)>1:
        print(f"{nn}: {list(zip(g['vendor_id'],g['vendor_name'],g['vat_id']))}")
# transactions & spend for the shared-VAT vendors
print("\n-- spend for V-0003/4/5 (Karrenbach) --")
for vid in ['V-0003','V-0004','V-0005']:
    s=gl[gl['vendor_id']==vid]
    print(f"{vid} {vinfo.loc[vid,'vendor_name']}: n={len(s)} total={s['amount_eur'].sum():.2f} accts={s['account'].value_counts().to_dict()} iban={vinfo.loc[vid,'iban']}")

print("\n\n###### 2. DETECTOR DISTRIBUTIONAL CHECK ######")
# per-vendor mean vs number of detector flags
dfl=gl[gl['txn_id'].isin(flagged_ids)].copy()
vmean=gl.groupby('vendor_id')['amount_eur'].mean()
vflag=dfl.groupby('vendor_id').size()
comp=pd.DataFrame({'vendor_mean':vmean,'n_flags':vflag}).fillna(0)
print("corr(vendor mean amount, n detector flags):", round(comp['vendor_mean'].corr(comp['n_flags']),3))
# are any detector-flagged txns on a non-allowed account, or above vendor's own non-flagged max?
allowed=vm.set_index('vendor_id')['allowed_accounts'].apply(lambda s:set(str(s).split(';'))).to_dict()
bad_acct=[t for t in flagged_ids if gl.loc[gl['txn_id']==t,'account'].iloc[0] not in allowed[gl.loc[gl['txn_id']==t,'vendor_id'].iloc[0]]]
print("detector-flagged txns on NON-allowed account:", len(bad_acct), bad_acct[:20])
# detector-flagged txns whose amount exceeds their vendor's max non-flagged amount
over=[]
for t in flagged_ids:
    row=gl[gl['txn_id']==t].iloc[0]; vs=gl[gl['vendor_id']==row['vendor_id']]
    if row['amount_eur']>=vs['amount_eur'].max()-1e-9 and len(vs)>3:
        over.append((t,row['vendor_id'],round(row['amount_eur'],2)))
print("detector-flagged txns that are their vendor's max amount:", len(over))

print("\n\n###### 3. THRESHOLD DISTRIBUTION (10,000 approval tier) ######")
for lo,hi in [(9000,9500),(9500,10000),(10000,10500),(10500,11000)]:
    n=((gl['amount_eur']>=lo)&(gl['amount_eur']<hi)).sum()
    print(f"  [{lo},{hi}): {n} txns")
print("txns >=10000:",(gl['amount_eur']>=10000).sum(), " total txns:",len(gl))
# how many DISTINCT vendors have >=10000 single invoices
big=gl[gl['amount_eur']>=10000]
print("vendors with >=10000 invoices:", big['vendor_id'].nunique(), "; their invoice count:", len(big))

print("\n\n###### 4. INVOICE NUMBER STRUCTURE (per vendor sequential?) ######")
# check for a few random vendors whether invoice numbers are strictly per-vendor sequential
for vid in ['V-0008','V-0029','V-0078','V-0157']:
    s=gl[gl['vendor_id']==vid].sort_values('posting_date')
    nums=pd.to_numeric(s['invoice_number'],errors='coerce')
    diffs=nums.diff().dropna()
    print(f"{vid}: invoice# range {nums.min():.0f}-{nums.max():.0f}, n={len(s)}, monotonic_incr={ (diffs>=0).all() }, all_step1={ (diffs==1).all() }")

print("\n\n###### 5. POSTING PATTERNS BY USER ######")
hu=gl[gl['posted_by']!='INTEG-01']
print("human posters totals:")
print(hu.groupby('posted_by').agg(n=('amount_eur','size'),total=('amount_eur','sum'),mean=('amount_eur','mean'),max=('amount_eur','max')).round(2))
print("\nnon-working-day postings by poster (INTEG exempt):")
wd=pd.read_csv(D/"company_calendar.csv"); wd['date']=pd.to_datetime(wd['date']); wdm=dict(zip(wd['date'],wd['is_working_day'].astype(str).str.strip().isin(['True'])))
gl['is_wd']=gl['posting_date'].map(wdm)
nwd=gl[(~gl['is_wd'])&(gl['posted_by']!='INTEG-01')]
print(nwd.groupby('posted_by').size())

print("\n\n###### 6. TOP SPEND MOVERS H1 vs H2 (by vendor) ######")
piv=gl.pivot_table(index='vendor_id',columns='half',values='amount_eur',aggfunc='sum',fill_value=0)
piv['delta']=piv.get('H2',0)-piv.get('H1',0)
piv['ratio']=(piv.get('H2',0)+1)/(piv.get('H1',0)+1)
piv['name']=piv.index.map(vinfo['vendor_name'])
print("Biggest absolute increases H1->H2:")
print(piv.sort_values('delta',ascending=False).head(8)[['name','H1','H2','delta','ratio']].round(0))
print("Biggest absolute decreases H1->H2:")
print(piv.sort_values('delta').head(8)[['name','H1','H2','delta','ratio']].round(0))
print("Largest ratio jumps (H1>2000):")
sub=piv[piv['H1']>2000]
print(sub.sort_values('ratio',ascending=False).head(8)[['name','H1','H2','delta','ratio']].round(2))

print("\n\n###### 7. MONTHLY TOTAL BY ACCOUNT-CLASS ######")
mt=gl.groupby('pmonth')['amount_eur'].sum().round(0)
print("monthly total spend:"); print(mt)
