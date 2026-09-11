import pandas as pd, json, numpy as np
from pathlib import Path

BASE = Path(r"C:\Users\luigi\Dropbox\Archivio famiglia\Hapax\Case Studies\06 Anomaly Detection")
OUT = BASE / "data/analysis/agent_runs/_scratch_run03"

gl = pd.read_csv(BASE/"data/gl_transactions.csv", dtype=str)
for c in ["amount_eur"]:
    gl[c] = gl[c].astype(float)
for c in ["posting_date","invoice_date","due_date"]:
    gl[c+"_d"] = pd.to_datetime(gl[c])
gl["month"] = gl["posting_date_d"].dt.month
vm = pd.read_csv(BASE/"data/vendor_master.csv", dtype=str)
coa = pd.read_csv(BASE/"data/chart_of_accounts.csv", dtype=str)
cal = pd.read_csv(BASE/"data/company_calendar.csv", dtype=str)
rf = pd.read_csv(BASE/"data/analysis/rule_flags.csv", dtype=str)
df = pd.read_csv(BASE/"data/analysis/detector_flags.csv")
clusters = json.load(open(BASE/"data/analysis/clusters.json"))

gl = gl.set_index("txn_id", drop=False)
rf_map = rf.groupby("txn_id")["test"].apply(list).to_dict()
det_map = df.set_index("txn_id").to_dict("index")
vm_map = vm.set_index("vendor_id").to_dict("index")
cal_map = cal.set_index("date")["is_working_day"].to_dict()
coa_map = coa.set_index("account")["name_en"].to_dict()

def wd(dstr):
    return cal_map.get(dstr, "??")

def txn_line(t):
    r = gl.loc[t]
    tests = rf_map.get(t, [])
    det = det_map.get(t)
    ds = f"score={det['anomaly_score']:.5f} rank={int(det['rank'])}" if det else ""
    return (f"  {t} post={r.posting_date}(wd={wd(r.posting_date)}) inv={r.invoice_date} due={r.due_date} "
            f"acct={r.account}({coa_map.get(r.account,'?')}) amt={r.amount_eur:.2f} "
            f"invno={r.invoice_number} by={r.posted_by} | {r.memo} | tests={tests} {ds}")

def vendor_block(vid):
    v = vm_map.get(vid)
    if not v: return f"  [vendor {vid} NOT IN MASTER]"
    sub = gl[gl.vendor_id==vid]
    return (f"  VENDOR {vid} {v['vendor_name']} country={v['country']} vat={v['vat_id']} iban={v['iban']}\n"
            f"    terms_days={v['terms_days']} allowed_accounts={v['allowed_accounts']} active_from={v['active_from']} addr={v['address']}\n"
            f"    total_txns={len(sub)} total_eur={sub.amount_eur.sum():.2f} accounts_used={sorted(sub.account.unique())}\n"
            f"    amt_stats: min={sub.amount_eur.min():.2f} med={sub.amount_eur.median():.2f} mean={sub.amount_eur.mean():.2f} max={sub.amount_eur.max():.2f}")

lines = []
def p(*a):
    lines.append(" ".join(str(x) for x in a))

p("="*100)
p("PER-UNIT DUMP")
p("="*100)
for u in clusters:
    p("\n" + "#"*90)
    p(f"UNIT {u['unit_id']} type={u['unit_type']} key={u.get('group_key')} stats={u['stats']}")
    vids = set()
    for t in u["txn_ids"]:
        if t in gl.index:
            vids.add(gl.loc[t].vendor_id)
    for vid in sorted(vids):
        p(vendor_block(vid))
    p("  --- flagged txns ---")
    for t in u["txn_ids"]:
        p(txn_line(t))

Path(OUT/"unit_dump.txt").write_text("\n".join(lines), encoding="utf-8")
print("wrote unit_dump.txt lines=", len(lines))
print("gl rows=", len(gl), " vendors=", len(vm), " rule_flags=", len(rf), " det_flags=", len(df))
print("unique flagged txns rule=", rf.txn_id.nunique(), " det=", df.txn_id.nunique())
