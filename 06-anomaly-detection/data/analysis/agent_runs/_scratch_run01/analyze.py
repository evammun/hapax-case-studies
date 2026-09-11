import json, sys
from pathlib import Path
import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 240)
pd.set_option('display.max_colwidth', 60)

BASE = Path(r"C:\Users\luigi\Dropbox\Archivio famiglia\Hapax\Case Studies\06 Anomaly Detection")
D = BASE / "data"
A = D / "analysis"

gl = pd.read_csv(D / "gl_transactions.csv", dtype={'invoice_number': str})
vm = pd.read_csv(D / "vendor_master.csv", dtype=str)
coa = pd.read_csv(D / "chart_of_accounts.csv", dtype={'account': str})
cal = pd.read_csv(D / "company_calendar.csv")
rf = pd.read_csv(A / "rule_flags.csv")
df_ = pd.read_csv(A / "detector_flags.csv")
clusters = json.loads((A / "clusters.json").read_text(encoding="utf-8"))

for c in ['posting_date','invoice_date','due_date']:
    gl[c] = pd.to_datetime(gl[c])
gl['account'] = gl['account'].astype(str)
gl['pmonth'] = gl['posting_date'].dt.month
cal['date'] = pd.to_datetime(cal['date'])
cal['is_working_day'] = cal['is_working_day'].astype(str).str.strip().isin(['True','true','TRUE'])
wd = dict(zip(cal['date'], cal['is_working_day']))
note = dict(zip(cal['date'], cal['note'].fillna('')))
gl['is_wd'] = gl['posting_date'].map(wd)
gl['cal_note'] = gl['posting_date'].map(note)

acct_name = dict(zip(coa['account'], coa['name_en']))
gl['acct_name'] = gl['account'].map(acct_name)

# vendor lookups
vm['allowed_set'] = vm['allowed_accounts'].apply(lambda s: set(str(s).split(';')))
vinfo = vm.set_index('vendor_id')
rf_map = dict(zip(rf['txn_id'], rf['test']))
score_map = dict(zip(df_['txn_id'], df_['anomaly_score']))
rank_map = dict(zip(df_['txn_id'], df_['rank']))

gl_by_id = gl.set_index('txn_id')

def vend_summary(vid):
    sub = gl[gl['vendor_id']==vid]
    r = vinfo.loc[vid]
    return {
        'vendor_id': vid, 'name': r['vendor_name'], 'country': r['country'],
        'terms_days': r['terms_days'], 'allowed': r['allowed_accounts'],
        'vat': r['vat_id'], 'iban': r['iban'],
        'n_txn': len(sub), 'total_eur': round(sub['amount_eur'].sum(),2),
        'mean_eur': round(sub['amount_eur'].mean(),2) if len(sub) else 0,
        'median_eur': round(sub['amount_eur'].median(),2) if len(sub) else 0,
        'accounts_used': sub['account'].value_counts().to_dict(),
        'posters': sub['posted_by'].value_counts().to_dict(),
    }

def dump_unit(u, extra_cols=None):
    cols = ['txn_id','posting_date','invoice_date','due_date','vendor_id','vendor_name','account','acct_name','amount_eur','invoice_number','posted_by','memo']
    ids = u['txn_ids']
    sub = gl_by_id.loc[[i for i in ids if i in gl_by_id.index]].reset_index()
    sub = sub.sort_values('posting_date')
    sub['test'] = sub['txn_id'].map(rf_map)
    sub['dscore'] = sub['txn_id'].map(score_map)
    sub['drank'] = sub['txn_id'].map(rank_map)
    print("="*130)
    print(f"UNIT {u['unit_id']}  type={u['unit_type']}  key={u.get('group_key')}  n_flags={u['stats'].get('n_flags')}  total={u['stats'].get('total_eur')}")
    print(f"  tests={u['stats'].get('tests_involved')}  score_range={u['stats'].get('score_range')}  months={u['stats'].get('months_touched')}")
    gk = u.get('group_key')
    if gk and gk.startswith('V-'):
        vs = vend_summary(gk)
        print(f"  VENDOR {gk}: {vs['name']} [{vs['country']}] terms={vs['terms_days']} allowed={vs['allowed']}")
        print(f"    all-year: n_txn={vs['n_txn']} total={vs['total_eur']} mean={vs['mean_eur']} median={vs['median_eur']}")
        print(f"    accounts_used(all yr)={vs['accounts_used']}")
        print(f"    posters(all yr)={vs['posters']}")
        print(f"    vat={vs['vat']} iban={vs['iban']}")
    showcols = ['txn_id','posting_date','invoice_date','due_date','account','amount_eur','invoice_number','posted_by','test','drank','dscore','memo']
    with pd.option_context('display.max_colwidth', 70):
        print(sub[showcols].to_string(index=False))
    return sub

print("\n\n############## GL OVERVIEW ##############")
print("rows:", len(gl), "vendors:", gl['vendor_id'].nunique(), "date range:", gl['posting_date'].min(), gl['posting_date'].max())
print("posters:", gl['posted_by'].value_counts().to_dict())
print("total spend:", round(gl['amount_eur'].sum(),2))

# process units
order = [u['unit_id'] for u in clusters]
print("\nUNIT ORDER:", order)

print("\n\n########## RULE UNITS (RU-01..RU-13) ##########")
for u in clusters:
    if u['unit_id'].startswith('RU-'):
        dump_unit(u)
