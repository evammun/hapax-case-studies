import pandas as pd, json, numpy as np
from pathlib import Path

BASE = Path(r"C:\Users\luigi\Dropbox\Archivio famiglia\Hapax\Case Studies\06 Anomaly Detection")
D = BASE / "data"
pd.set_option('display.width', 200)
pd.set_option('display.max_columns', 40)
pd.set_option('display.max_colwidth', 60)

gl = pd.read_csv(D/"gl_transactions.csv", dtype={'account':str})
vm = pd.read_csv(D/"vendor_master.csv", dtype={'allowed_accounts':str})
coa = pd.read_csv(D/"chart_of_accounts.csv", dtype={'account':str})
cal = pd.read_csv(D/"company_calendar.csv")
rf = pd.read_csv(D/"analysis/rule_flags.csv")
df = pd.read_csv(D/"analysis/detector_flags.csv")
clusters = json.load(open(D/"analysis/clusters.json", encoding='utf-8'))

for c in ['posting_date','invoice_date','due_date']:
    gl[c] = pd.to_datetime(gl[c])
gl['pmonth'] = gl['posting_date'].dt.month
cal['date'] = pd.to_datetime(cal['date'])
workday = dict(zip(cal['date'], cal['is_working_day']))
gl['post_is_workday'] = gl['posting_date'].map(workday)

acct_name = dict(zip(coa['account'], coa['name_en']))
gl = gl.merge(vm[['vendor_id','allowed_accounts','terms_days','country','iban','vat_id']], on='vendor_id', how='left')

print("=== GL shape:", gl.shape)
print("=== posters distribution ===")
print(gl['posted_by'].value_counts().head(20))
print("=== total by account ===")
tot = gl.groupby('account')['amount_eur'].agg(['count','sum']).sort_values('sum', ascending=False)
tot['name'] = tot.index.map(acct_name)
print(tot.head(45).to_string())

# helper to dump a unit
gli = gl.set_index('txn_id')
def dump_unit(u):
    print("\n" + "="*90)
    print(f"UNIT {u['unit_id']}  type={u['unit_type']}  key={u.get('group_key')}  stats={u['stats']}")
    txns = u['txn_ids']
    sub = gli.loc[[t for t in txns if t in gli.index]].copy()
    sub = sub.sort_values('posting_date')
    cols = ['posting_date','invoice_date','due_date','vendor_id','vendor_name','account','amount_eur','invoice_number','posted_by','memo']
    print(sub[cols].to_string())
    # vendor context
    for vid in sub['vendor_id'].unique():
        vh = gl[gl['vendor_id']==vid]
        vrow = vm[vm['vendor_id']==vid].iloc[0]
        print(f"  -- vendor {vid} {vrow['vendor_name']} country={vrow['country']} terms={vrow['terms_days']} allowed={vrow['allowed_accounts']}")
        print(f"     full-year: n={len(vh)} sum={vh['amount_eur'].sum():.2f} mean={vh['amount_eur'].mean():.2f} min={vh['amount_eur'].min():.2f} max={vh['amount_eur'].max():.2f}")
        print(f"     accounts used: {vh['account'].value_counts().to_dict()}")
        print(f"     posters: {vh['posted_by'].value_counts().to_dict()}")
    return sub

for u in clusters:
    dump_unit(u)
