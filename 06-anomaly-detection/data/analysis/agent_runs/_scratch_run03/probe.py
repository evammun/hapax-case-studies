import pandas as pd
from pathlib import Path
pd.set_option("display.width",220)
BASE = Path(r"C:\Users\luigi\Dropbox\Archivio famiglia\Hapax\Case Studies\06 Anomaly Detection")
gl = pd.read_csv(BASE/"data/gl_transactions.csv", dtype=str); gl["amount_eur"]=gl["amount_eur"].astype(float)
vm = pd.read_csv(BASE/"data/vendor_master.csv", dtype=str)
df = pd.read_csv(BASE/"data/analysis/detector_flags.csv"); rf=pd.read_csv(BASE/"data/analysis/rule_flags.csv",dtype=str)
detset=set(df.txn_id); rfset=set(rf.txn_id)

print("=== KARRENBACH TRIO (shared VAT DE199283746) ===")
for vid in ["V-0003","V-0004","V-0005"]:
    v=vm[vm.vendor_id==vid].iloc[0]; sub=gl[gl.vendor_id==vid]
    print(f"{vid} name='{v.vendor_name}' iban={v.iban} allowed={v.allowed_accounts} active={v.active_from}")
    print(f"    txns={len(sub)} eur={sub.amount_eur.sum():.2f} months={sorted(pd.to_datetime(sub.posting_date).dt.month.unique())} "
          f"accts={sorted(sub.account.unique())} amt[min/med/max]={sub.amount_eur.min():.2f}/{sub.amount_eur.median():.2f}/{sub.amount_eur.max():.2f}")
    print(f"    any detector-flagged: {sum(t in detset for t in sub.txn_id)}  any rule-flagged: {sum(t in rfset for t in sub.txn_id)}")
    print("    sample memos:", list(sub.memo.head(3)))

print("\n=== V-0019 (single big H2 invoice) ===")
s=gl[gl.vendor_id=="V-0019"]
print(vm[vm.vendor_id=="V-0019"][["vendor_name","country","allowed_accounts","terms_days","active_from"]].to_string(index=False))
print(s[["txn_id","posting_date","account","amount_eur","invoice_number","posted_by","memo"]].to_string(index=False))
print("in detector?", set(s.txn_id)&detset, "in rule?", set(s.txn_id)&rfset)

print("\n=== single-invoice vendors with amount>=10000 (new/one-off big) ===")
cnt=gl.groupby("vendor_id").size()
one=cnt[cnt==1].index
big=gl[(gl.vendor_id.isin(one))&(gl.amount_eur>=8000)]
print(big[["vendor_id","posting_date","account","amount_eur","posted_by","memo"]].to_string(index=False))

print("\n=== confirm near-dup name pairs do NOT share vat or iban (only trio shares vat) ===")
import re
def norm(n):
    s=n.lower()
    for suf in [" oy ab"," oy"," ab"," tmi"," ky"," as","gmbh"]: s=s.replace(suf,"")
    return re.sub(r"[^a-z0-9]","",s)
vm["nname"]=vm.vendor_name.map(norm)
for nn,grp in vm[vm.duplicated("nname",keep=False)].groupby("nname"):
    vats=grp.vat_id.nunique(); ibans=grp.iban.nunique()
    flag="<-- SHARES VAT" if vats<len(grp) else ("<-- SHARES IBAN" if ibans<len(grp) else "")
    if flag: print(nn, list(grp.vendor_id), "vat_uniq",vats,"iban_uniq",ibans, flag)
print("(only printed pairs that share vat/iban; blank above = none beyond trio)")

print("\n=== RU-01 V-0006: does account 7100 exist for peer marketing vendors? ===")
mk=gl[gl.account=="7100"]
print("distinct vendors booking to 7100:", mk.vendor_id.nunique(), "sample:", sorted(mk.vendor_id.unique())[:8])
print("V-0006 all rows account/memo:")
print(gl[gl.vendor_id=="V-0006"][["posting_date","account","amount_eur","posted_by","memo"]].to_string(index=False))
