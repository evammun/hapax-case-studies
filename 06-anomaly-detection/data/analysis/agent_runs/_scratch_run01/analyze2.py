import json
from pathlib import Path
import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None); pd.set_option('display.width', 260); pd.set_option('display.max_colwidth', 60)
BASE = Path(r"C:\Users\luigi\Dropbox\Archivio famiglia\Hapax\Case Studies\06 Anomaly Detection")
D = BASE/"data"; A = D/"analysis"
gl = pd.read_csv(D/"gl_transactions.csv", dtype={'invoice_number':str})
vm = pd.read_csv(D/"vendor_master.csv", dtype=str)
coa = pd.read_csv(D/"chart_of_accounts.csv", dtype={'account':str})
cal = pd.read_csv(D/"company_calendar.csv")
rf = pd.read_csv(A/"rule_flags.csv"); df_ = pd.read_csv(A/"detector_flags.csv")
clusters = json.loads((A/"clusters.json").read_text(encoding="utf-8"))
for c in ['posting_date','invoice_date','due_date']: gl[c]=pd.to_datetime(gl[c])
gl['account']=gl['account'].astype(str); gl['pmonth']=gl['posting_date'].dt.month
cal['date']=pd.to_datetime(cal['date']); cal['is_working_day']=cal['is_working_day'].astype(str).str.strip().isin(['True'])
wd=dict(zip(cal['date'],cal['is_working_day']))
gl['is_wd']=gl['posting_date'].map(wd)
acct_name=dict(zip(coa['account'],coa['name_en'])); gl['acct_name']=gl['account'].map(acct_name)
vinfo=vm.set_index('vendor_id')
score_map=dict(zip(df_['txn_id'],df_['anomaly_score'])); rank_map=dict(zip(df_['txn_id'],df_['rank']))
rf_map=dict(zip(rf['txn_id'],rf['test']))
gl_by_id=gl.set_index('txn_id')

def dump_det(u):
    gk=u['group_key']; ids=u['txn_ids']
    print("="*130)
    print(f"UNIT {u['unit_id']}  key={gk}  n_flags={u['stats']['n_flags']}  total={u['stats']['total_eur']}  score_range={u['stats'].get('score_range')}")
    if gk and gk.startswith('V-'):
        allsub=gl[gl['vendor_id']==gk]
        r=vinfo.loc[gk]
        print(f"  VENDOR {gk}: {r['vendor_name']} [{r['country']}] terms={r['terms_days']} allowed={r['allowed_accounts']}")
        print(f"    ALL-YEAR profile: n={len(allsub)} total={allsub['amount_eur'].sum():.2f} mean={allsub['amount_eur'].mean():.2f} median={allsub['amount_eur'].median():.2f} min={allsub['amount_eur'].min():.2f} max={allsub['amount_eur'].max():.2f}")
        print(f"    accounts(all yr)={allsub['account'].value_counts().to_dict()}")
        print(f"    posters(all yr)={allsub['posted_by'].value_counts().to_dict()}")
        print(f"    n flagged {len(ids)} of {len(allsub)} txns")
    sub=gl_by_id.loc[[i for i in ids if i in gl_by_id.index]].reset_index().sort_values('posting_date')
    sub['drank']=sub['txn_id'].map(rank_map); sub['dscore']=sub['txn_id'].map(score_map); sub['rule']=sub['txn_id'].map(rf_map)
    cols=['txn_id','posting_date','vendor_id','account','amount_eur','invoice_number','posted_by','drank','rule','memo']
    with pd.option_context('display.max_colwidth',65):
        print(sub[cols].to_string(index=False))

print("########## DETECTOR UNITS ##########")
for u in clusters:
    if u['unit_id'].startswith('DU-'): dump_det(u)

print("\n\n########## SINGLES ##########")
for u in clusters:
    if u['unit_id']=='SINGLES':
        ids=u['txn_ids']
        sub=gl_by_id.loc[ids].reset_index()
        sub['drank']=sub['txn_id'].map(rank_map); sub['dscore']=sub['txn_id'].map(score_map); sub['rule']=sub['txn_id'].map(rf_map)
        sub['vname']=sub['vendor_id'].map(vinfo['vendor_name']); sub['allowed']=sub['vendor_id'].map(vinfo['allowed_accounts'])
        sub=sub.sort_values('drank')
        for _,row in sub.iterrows():
            vsub=gl[gl['vendor_id']==row['vendor_id']]
            print(f"\n-- {row['txn_id']} rank{int(row['drank'])} score={row['dscore']:.4f} vendor={row['vendor_id']} {row['vname']} allowed={row['allowed']}")
            print(f"   acct={row['account']}({acct_name.get(row['account'])}) amt={row['amount_eur']} poster={row['posted_by']} date={row['posting_date'].date()} wd={row['is_wd']} rule={row['rule']}")
            print(f"   memo={row['memo']!r}")
            print(f"   vendor profile: n={len(vsub)} mean={vsub['amount_eur'].mean():.2f} median={vsub['amount_eur'].median():.2f} max={vsub['amount_eur'].max():.2f} accts={vsub['account'].value_counts().to_dict()}")
