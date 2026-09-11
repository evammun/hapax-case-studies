import pandas as pd, json, numpy as np
from pathlib import Path
pd.set_option("display.width",200); pd.set_option("display.max_rows",300); pd.set_option("display.max_columns",40)

BASE = Path(r"C:\Users\luigi\Dropbox\Archivio famiglia\Hapax\Case Studies\06 Anomaly Detection")
gl = pd.read_csv(BASE/"data/gl_transactions.csv", dtype=str)
gl["amount_eur"]=gl["amount_eur"].astype(float)
gl["posting_date_d"]=pd.to_datetime(gl["posting_date"])
gl["month"]=gl["posting_date_d"].dt.month
vm = pd.read_csv(BASE/"data/vendor_master.csv", dtype=str)
cal = pd.read_csv(BASE/"data/company_calendar.csv", dtype=str)
rf = pd.read_csv(BASE/"data/analysis/rule_flags.csv", dtype=str)
df = pd.read_csv(BASE/"data/analysis/detector_flags.csv")
cal_map = cal.set_index("date")["is_working_day"].to_dict()
gl["is_wd"]=gl["posting_date"].map(cal_map)

print("=== rule_flags counts by test ===")
print(rf["test"].value_counts())
print("total rule flags:", len(rf), "unique txns:", rf.txn_id.nunique())

print("\n=== VENDOR MASTER HYGIENE ===")
print("n vendors:", len(vm))
# byte-identical names
dupn = vm[vm.duplicated("vendor_name",keep=False)].sort_values("vendor_name")
print("\n-- byte-identical vendor_name across ids --")
print(dupn[["vendor_id","vendor_name","country","vat_id","iban"]].to_string(index=False) if len(dupn) else "NONE")
# shared IBAN
dupi = vm[vm.duplicated("iban",keep=False)].sort_values("iban")
print("\n-- shared IBAN across different vendor_id --")
print(dupi[["vendor_id","vendor_name","iban","vat_id"]].to_string(index=False) if len(dupi) else "NONE")
# shared VAT
dupv = vm[vm.duplicated("vat_id",keep=False)].sort_values("vat_id")
print("\n-- shared vat_id across different vendor_id --")
print(dupv[["vendor_id","vendor_name","vat_id","iban"]].to_string(index=False) if len(dupv) else "NONE")
# near-duplicate names (normalized: strip corporate suffixes, lowercase)
import re
def norm(n):
    s=n.lower()
    for suf in [" oy ab"," oy"," ab"," tmi"," ky"," as","gmbh"]:
        s=s.replace(suf,"")
    s=re.sub(r"[^a-zäöå0-9]","",s)
    return s.strip()
vm["nname"]=vm.vendor_name.map(norm)
nd = vm[vm.duplicated("nname",keep=False)].sort_values("nname")
print("\n-- near-duplicate normalized names --")
print(nd[["vendor_id","vendor_name","nname","country","iban"]].to_string(index=False) if len(nd) else "NONE")

print("\n=== POSTING PATTERNS BY USER ===")
g=gl.groupby("posted_by").agg(n=("txn_id","size"), eur=("amount_eur","sum"),
     wknd=("is_wd", lambda s:(s=="False").sum())).sort_values("n",ascending=False)
g["wknd_pct"]=(g["wknd"]/g["n"]*100).round(1)
print(g.head(40).to_string())
print("\nhuman (non-INTEG) posters weekend rows (calendar-rule candidates):")
hum=gl[gl.posted_by!="INTEG-01"]
print("human rows total:", len(hum), " on non-working days:", (hum.is_wd=="False").sum())
print(hum[hum.is_wd=="False"].groupby("posted_by").size().sort_values(ascending=False).to_string())

print("\n=== U-117 detail ===")
u=gl[gl.posted_by=="U-117"]
print("U-117 total posts:", len(u), "eur:", round(u.amount_eur.sum(),2), "weekend:", (u.is_wd=="False").sum(),
      "months:", sorted(u.month.unique()))
print("U-117 vendors:", sorted(u.vendor_id.unique()))

print("\n=== NEAR-THRESHOLD SWEEP (9500-9999.99) whole ledger ===")
nt=gl[(gl.amount_eur>=9500)&(gl.amount_eur<10000)]
print("count:", len(nt))
print(nt.groupby("vendor_id").agg(n=("txn_id","size"),amounts=("amount_eur",lambda s:sorted(round(x,2) for x in s))).to_string())

print("\n=== OVER-THRESHOLD (>=10000) ===")
ot=gl[gl.amount_eur>=10000]
print("count invoices >=10000:", len(ot))
print(ot.groupby("vendor_id").agg(n=("txn_id","size"),mx=("amount_eur","max")).sort_values("n",ascending=False).head(20).to_string())

print("\n=== SPLIT SWEEP: same vendor, parts 4000-9999.99, <=3 days apart, sum>=10000 ===")
cand=gl[(gl.amount_eur>=4000)&(gl.amount_eur<10000)].sort_values(["vendor_id","posting_date_d"])
hits=[]
for vid,sub in cand.groupby("vendor_id"):
    rows=sub.to_dict("records")
    for i in range(len(rows)):
        for j in range(i+1,len(rows)):
            dd=abs((rows[j]["posting_date_d"]-rows[i]["posting_date_d"]).days)
            if dd>3: break
            if rows[i]["amount_eur"]+rows[j]["amount_eur"]>=10000:
                hits.append((vid,rows[i]["txn_id"],rows[j]["txn_id"],round(rows[i]["amount_eur"],2),round(rows[j]["amount_eur"],2),dd))
print("split candidate pairs found:", len(hits))
for h in hits: print(h)

print("\n=== MONTHLY TOTALS BY ACCOUNT CLASS (top accounts) ===")
gl["ym"]=gl.posting_date_d.dt.month
piv=gl.pivot_table(index="account",columns="ym",values="amount_eur",aggfunc="sum",fill_value=0)
piv["TOTAL"]=piv.sum(axis=1)
print(piv.sort_values("TOTAL",ascending=False).head(12).round(0).to_string())

print("\n=== TOP SPEND MOVERS H1 vs H2 by vendor ===")
gl["half"]=np.where(gl.month<=6,"H1","H2")
hv=gl.pivot_table(index="vendor_id",columns="half",values="amount_eur",aggfunc="sum",fill_value=0)
hv["delta"]=hv.get("H2",0)-hv.get("H1",0)
hv["tot"]=hv.get("H1",0)+hv.get("H2",0)
hv["h2_over_h1"]=(hv.get("H2",0)/hv.get("H1",0).replace(0,np.nan)).round(2)
print("-- biggest H2>H1 increases --")
print(hv.sort_values("delta",ascending=False).head(12).round(0).to_string())
print("-- biggest H2<H1 decreases --")
print(hv.sort_values("delta").head(12).round(0).to_string())

print("\n=== SINGLES txn -> vendor mapping w/ vendor max ===")
singles=["TXN002850","TXN002870","TXN006870","TXN010666","TXN025791","TXN044434","TXN044442","TXN045742","TXN047046","TXN048135"]
gi=gl.set_index("txn_id")
for t in singles:
    r=gi.loc[t]; vsub=gl[gl.vendor_id==r.vendor_id]
    print(f"{t} v={r.vendor_id} {r.vendor_name[:22]:22} acct={r.account} amt={r.amount_eur:.2f} vmax={vsub.amount_eur.max():.2f} vmed={vsub.amount_eur.median():.2f} n={len(vsub)}")

print("\n=== check V-0006 (RU-01) allowed vs used + is 7100 used elsewhere ===")
v6=vm[vm.vendor_id=="V-0006"][["allowed_accounts"]]
print("V-0006 allowed:", v6.values, " used:", sorted(gl[gl.vendor_id=='V-0006'].account.unique()))
print("account 7100 (Marketing) total rows in ledger:", (gl.account=='7100').sum(), " 7200 rows:", (gl.account=='7200').sum())
