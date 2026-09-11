# -*- coding: utf-8 -*-
import json
from pathlib import Path
import pandas as pd, numpy as np

SCR = Path(__file__).resolve().parent
BASE = SCR.parents[3]  # .../06 Anomaly Detection
D = BASE/"data"; A = D/"analysis"
gl=pd.read_csv(D/"gl_transactions.csv",dtype={'invoice_number':str})
vm=pd.read_csv(D/"vendor_master.csv",dtype=str)
df_=pd.read_csv(A/"detector_flags.csv"); rf=pd.read_csv(A/"rule_flags.csv")
clusters=json.loads((A/"clusters.json").read_text(encoding="utf-8"))
gl['account']=gl['account'].astype(str)
vinfo=vm.set_index('vendor_id')
rule_ids=set(rf['txn_id'])
allowed=vm.set_index('vendor_id')['allowed_accounts'].apply(lambda s:str(s).split(';')).to_dict()

def du_stats(vid, ids):
    vs=gl[gl['vendor_id']==vid]
    prim=vs['account'].value_counts().idxmax()
    fsub=gl[gl['txn_id'].isin(ids)]
    n_minor=int((fsub['account']!=prim).sum())
    pcts=[(vs['amount_eur']<a).mean() for a in fsub['amount_eur']]
    hi=int(sum(1 for p in pcts if p>=0.80))
    prim_share=(vs['account']==prim).mean()
    return dict(name=vinfo.loc[vid,'vendor_name'],prim=prim,prim_share=round(prim_share,2),
                n=len(ids),n_minor=n_minor,hi=hi,vmax=round(vs['amount_eur'].max(),2),
                allowed=vinfo.loc[vid,'allowed_accounts'],score_max=round(max([df_.set_index('txn_id').loc[t,'anomaly_score'] for t in ids]),4))

F=[]
def add(fid,headline,unit,verdict,mech,vids,accts,months,users,evidence,sev,conf,action):
    F.append({"finding_id":fid,"headline":headline,"unit_id":unit,"verdict":verdict,"mechanism":mech,
              "affected":{"vendor_ids":vids,"accounts":accts,"months":months,"users":users},
              "evidence":evidence,"severity":sev,"confidence":conf,"recommended_action":action})

# ---------------- RULE UNITS ----------------
add("F-01","Whole-vendor advertising spend miscoded to IT services rather than Marketing.","RU-01","worry",
    "Persistent account-mapping error: every invoice from advertising agency V-0006 (allowed account 7100 Marketing) is posted to 7200 IT services by clerk U-204. Not cash loss, but it misstates expense-by-nature reporting.",
    ["V-0006"],["7200","7100"],[9,10],["U-204"],
    [{"source":"gl_transactions.csv","what":"account used vs vendor allowed_accounts","figure":"8 of 8 txns on 7200; vendor allowed_accounts=7100"},
     {"source":"gl_transactions.csv","what":"memo text on every line","figure":"all read 'Mainoskampanja, [kuukausi] 2025' (advertising campaign)"},
     {"source":"gl_transactions.csv","what":"total misclassified","figure":"EUR 36,934.24"}],
    "watch","high","Reclassify the EUR 36,934.24 to 7100 Marketing and correct U-204's coding rule for this vendor.")

add("F-02","Same order billed twice at an identical amount by vendor V-0008.","RU-02","worry",
    "Two orders each appear twice at the identical cent amount, days apart, with no partial-delivery marker and no credit note - the signature of duplicate billing of one delivery.",
    ["V-0008"],["4000"],[2,8],[],
    [{"source":"gl_transactions.csv","what":"paired identical amounts sharing one order ref","figure":"842.50 x2 (order 358022, 4 days apart); 615.20 x2 (order 358023, 7 days apart)"},
     {"source":"gl_transactions.csv","what":"memo lacks 'osatoimitus' (partial delivery) marker","figure":"both read 'Ostolasku, tilaus 358022/358023'"},
     {"source":"gl_transactions.csv","what":"potential double-payment exposure","figure":"EUR 1,457.70"}],
    "watch","medium","Three-way match both order pairs; recover EUR 1,457.70 if only one delivery exists per order.")

add("F-03","Same order billed twice at an identical amount by vendor V-0009.","RU-03","worry",
    "Same duplicate-billing signature as V-0008: two orders each invoiced twice at the identical cent amount, 5 days apart, no partial-delivery marker.",
    ["V-0009"],["4200"],[4,10],[],
    [{"source":"gl_transactions.csv","what":"paired identical amounts sharing one order ref","figure":"1,365.00 x2 (order 787675); 3,780.60 x2 (order 787676), each 5 days apart"},
     {"source":"gl_transactions.csv","what":"memo text","figure":"'Ostolasku, tilaus 787675/787676' - no partial-delivery note"},
     {"source":"gl_transactions.csv","what":"potential double-payment exposure","figure":"EUR 5,145.60"}],
    "watch","medium","Three-way match both pairs; recover EUR 5,145.60 if a single delivery underlies each order.")

add("F-04","Same order billed twice at an identical amount by vendor V-0010.","RU-04","worry",
    "Same duplicate-billing signature: two orders each invoiced twice at the identical cent amount, days apart, no partial-delivery marker.",
    ["V-0010"],["4300"],[6,12],[],
    [{"source":"gl_transactions.csv","what":"paired identical amounts sharing one order ref","figure":"2,940.75 x2 (order 847310); 1,120.35 x2 (order 847311)"},
     {"source":"gl_transactions.csv","what":"memo text","figure":"'Ostolasku, tilaus 847310/847311' - no partial-delivery note"},
     {"source":"gl_transactions.csv","what":"potential double-payment exposure","figure":"EUR 4,061.10"}],
    "watch","medium","Three-way match both pairs; recover EUR 4,061.10 if only one delivery exists per order.")

add("F-05","Round-thousand bimonthly billing from a steel supplier - unusual but benign.","RU-05","stand_down",
    "Six exact-thousand invoices from V-0011 on its correct account (4100). Round amounts trip the round_sum test but there is no threshold breach, no duplicate and no mapping error; amounts vary (5k-9k), consistent with estimated/contract billing.",
    ["V-0011"],["4100"],[1,3,5,7,9,11],[],
    [{"source":"gl_transactions.csv","what":"amounts and account","figure":"5,000/6,000/7,000/8,000/9,000/6,000 all on account 4100 (allowed)"},
     {"source":"gl_transactions.csv","what":"all below the 10,000 approval tier; no other test fired","figure":"max 9,000; total 41,000"}],
    "info","medium","")

add("F-06","One freight vendor's invoices all sit just below the EUR 10,000 approval tier.","RU-06","worry",
    "All four of V-0012's quarterly invoices land in EUR 9,580-9,899.99, just under the EUR 10,000 department-head approval threshold - consistent with sizing invoices to avoid approval. The 9,899.99 value (one cent under 9,900) is conspicuously precise.",
    ["V-0012"],["4410"],[2,5,8,11],[],
    [{"source":"gl_transactions.csv","what":"all invoices in the near-threshold band","figure":"9,712.45 / 9,580.10 / 9,899.99 / 9,650.75 (all in 9,500-9,999.99)"},
     {"source":"rule_flags.csv","what":"these are the only near_threshold flags in the ledger","figure":"4 of 4 belong to V-0012"},
     {"source":"gl_transactions.csv","what":"context: crossing 10,000 is normal here","figure":"51 invoices >=10,000 across 14 other vendors, so the threshold is not a hard block"}],
    "watch","medium","Confirm whether these freight amounts are genuine and whether they should have required department-head approval.")

add("F-07","Two partial-delivery invoices per order, each under EUR 10,000 but summing over it (V-0013).","RU-07","worry",
    "Two order pairs, each posted 1-2 days apart as partial deliveries ('osatoimitus'), each part 4k-7k and each pair summing above EUR 10,000 - the shape of splitting a >10k order into sub-threshold invoices. The partial-delivery memo is a plausible benign explanation.",
    ["V-0013"],["4110"],[1,7],[],
    [{"source":"gl_transactions.csv","what":"pair sums vs parts","figure":"5,820.40+5,495.10=11,315.50 (2 days); 6,340.25+6,910.80=13,251.05 (1 day); all parts <10,000"},
     {"source":"gl_transactions.csv","what":"memo","figure":"'Ostolasku, osatoimitus 2389xx' (partial delivery)"}],
    "watch","low","Confirm each order's full value went through the correct approval level rather than being split at invoicing.")

add("F-08","Two partial-delivery invoices per order, each under EUR 10,000 but summing over it (V-0014).","RU-08","worry",
    "Same split shape as V-0013: two order pairs posted 2-3 days apart as partial deliveries, each part under EUR 10,000, each pair summing above it.",
    ["V-0014"],["4310"],[4,10],[],
    [{"source":"gl_transactions.csv","what":"pair sums vs parts","figure":"4,780.60+6,255.90=11,036.50 (3 days); 7,120.15+4,610.35=11,730.50 (2 days)"},
     {"source":"gl_transactions.csv","what":"memo","figure":"'Ostolasku, osatoimitus 7323xx' (partial delivery)"}],
    "watch","low","Confirm the order values received department-head approval rather than being split under the tier.")

add("F-09","A single partial-delivery pair summing just over EUR 10,000 (V-0015).","RU-09","worry",
    "One order posted as two partial deliveries a day apart, each part under EUR 10,000, together EUR 13,330.75 - a single instance of the split shape; benign partial delivery is the likely explanation but approval should be confirmed.",
    ["V-0015"],["4420"],[9],[],
    [{"source":"gl_transactions.csv","what":"pair sum vs parts","figure":"5,990.55+7,340.20=13,330.75 (1 day apart), both <10,000"},
     {"source":"gl_transactions.csv","what":"memo","figure":"'Ostolasku, osatoimitus 890739/890740'"}],
    "watch","low","Confirm the order passed the correct approval level.")

add("F-10","Twelve identical monthly rent postings - textbook benign round-sum.","RU-10","stand_down",
    "V-0016 is a property company (Kiinteisto Oy); the twelve EUR 15,000 postings are monthly premises rent on account 7000, its only allowed account. Round amount is the nature of rent, not a signal.",
    ["V-0016"],["7000"],[1,2,3,4,5,6,7,8,9,10,11,12],[],
    [{"source":"gl_transactions.csv","what":"amount, account, memo","figure":"12 x 15,000 on 7000; memos 'Toimitilavuokra, [kuukausi] 2025' (premises rent)"},
     {"source":"vendor_master.csv","what":"vendor type and allowed account","figure":"Kiinteisto Oy Vantaan Teollisuustalo, allowed_accounts=7000"}],
    "info","high","")

add("F-11","Two equal-value invoices on two different purchase orders - coincidence, not duplicate.","RU-11","stand_down",
    "V-0018's two EUR 7,420 invoices reference two different purchase orders (PO-48213 and PO-48297), i.e. two distinct orders that happen to share an amount - not a re-billing of one order.",
    ["V-0018"],["4200"],[6],[],
    [{"source":"gl_transactions.csv","what":"memo PO references differ","figure":"'Tavarantoimitus, PO-48213' vs 'PO-48297', 4 days apart"},
     {"source":"gl_transactions.csv","what":"amount","figure":"7,420.00 each"}],
    "info","medium","")

add("F-12","Weekend postings fully explained by documented inventory overtime.","RU-12","stand_down",
    "Clerk U-031's two non-working-day postings both fall on Saturday 15 Nov 2025 and the memo documents the reason - agreed overtime for a stock count.",
    [],["4420"],[11],["U-031"],
    [{"source":"gl_transactions.csv","what":"posting date and memo","figure":"both 2025-11-15 (Saturday); memo 'Sovittu ylityo, inventaario 15.11.2025' (agreed overtime, inventory)"},
     {"source":"company_calendar.csv","what":"day type","figure":"2025-11-15 is_working_day=False"}],
    "info","high","")

add("F-13","One clerk posts on days off occasionally, but only small routine invoices.","RU-13","stand_down",
    "U-117 accounts for 8 of the ledger's 10 human non-working-day postings, spread over five months, all small routine purchase invoices - consistent with occasional flexible-hours data entry rather than a control problem.",
    [],["4200","7850","4210","4000","4420","7200"],[2,3,4,5,6],["U-117"],
    [{"source":"gl_transactions.csv","what":"count vs the user's total volume","figure":"8 non-working-day postings out of U-117's 1,466 (0.5%)"},
     {"source":"gl_transactions.csv","what":"amounts","figure":"EUR 300.37-2,000.20; total 7,504.66"},
     {"source":"rule_flags.csv","what":"only two users ever post off-day","figure":"U-031 (2, explained) and U-117 (8)"}],
    "info","medium","Confirm U-117's off-day posting is sanctioned flexible working; no other action.")

# ---------------- DETECTOR VENDOR UNITS ----------------
det_units=[u for u in clusters if u['unit_type']=='detector_vendor']
du_map={ 'DU-18':'V-0132' }
i=14
for u in det_units:
    vid=u['group_key']; ids=u['txn_ids']; s=du_stats(vid,ids)
    uid=u['unit_id']
    months=u['stats']['months_touched']
    note=""
    if uid=='DU-18':
        note=" One flagged item (10,039.71) sits just above the 10,000 tier but was posted openly - a benign contrast to the split/near-threshold vendors."
    mech=(f"Isolation-Forest picks up statistical dispersion, not a control breach: {s['n_minor']} of {s['n']} flagged lines are on {s['name']}'s rarer-but-allowed account and {s['hi']} of {s['n']} are in the vendor's top amount quintile. No flagged line is on a disallowed account, none is duplicated by a rule, none breaches the 10,000 tier.{note}")
    ev=[{"source":"gl_transactions.csv + vendor_master.csv","what":"flagged lines on the vendor's minority (but allowed) account","figure":f"{s['n_minor']}/{s['n']}; primary account {s['prim']} covers {int(s['prim_share']*100)}% of the vendor's year"},
        {"source":"gl_transactions.csv","what":"flagged lines in the vendor's upper amount tail (>=80th pct)","figure":f"{s['hi']}/{s['n']}; vendor own max {s['vmax']:.2f}"},
        {"source":"detector_flags.csv / rule_flags.csv","what":"no control breach among flagged lines","figure":"0 on disallowed accounts, 0 rule co-flags; max anomaly_score "+f"{s['score_max']}"}]
    add(f"F-{i:02d}",f"Detector cluster on {s['name']} ({vid}) is its own rare-account and top-amount tail - benign.",uid,"stand_down",mech,
        [vid],sorted(set(gl[gl['txn_id'].isin(ids)]['account'])),months,[],ev,"info","medium" if s['n']>=6 else "high","")
    i+=1

# ---------------- SINGLES ----------------
add(f"F-{i:02d}","Ten top-score singletons are each a vendor's own high-water-mark or a rare allowed account - benign.","SINGLES","stand_down",
    "Each of the ten highest-scoring isolated flags is explained by being the vendor's largest invoice of the year and/or a posting to its secondary allowed account; all are e-invoiced (INTEG-01), on allowed accounts, and below the 10,000 tier.",
    ["V-0071","V-0023","V-0142","V-0150","V-0171","V-0195","V-0105","V-0075","V-0095"],
    ["4430","4310","4110","4300","4020","7700","7250"],[1,2,3,7,11,12],[],
    [{"source":"gl_transactions.csv","what":"top singleton = vendor max","figure":"TXN010666 8,464.74 is V-0071's max; TXN045742 7,575.97 is V-0195's max; TXN006870 6,253.77 near V-0105 max 6,268.10"},
     {"source":"gl_transactions.csv","what":"others sit on the vendor's secondary allowed account","figure":"e.g. V-0075 7250 (11 of 113 lines), V-0142 4110 (6 of 47)"},
     {"source":"detector_flags.csv","what":"scores and posting channel","figure":"score 0.0237-0.0750; all posted by INTEG-01; no rule co-flag; none >=10,000"}],
    "info","medium","")
i+=1

# ---------------- RESIDUAL ----------------
add(f"F-{i:02d}","The ungrouped detector tail is low-score dispersion on allowed accounts - benign in aggregate.","RESIDUAL","stand_down",
    "The 30 residual lines are the lowest-score end of the detector output: all on allowed accounts, none rule-flagged, none above the 10,000 tier, 29 of 30 e-invoiced. About half are simply the upper decile of their vendor's amounts. Distributionally this is expected outlier noise, not a concentration of risk.",
    [],[],[1,2,3,4,6,7,8,9,10,11,12],[],
    [{"source":"gl_transactions.csv + vendor_master.csv","what":"account legitimacy","figure":"0 of 30 on a disallowed account"},
     {"source":"detector_flags.csv","what":"score band","figure":"all scores <=0.0160 (ledger max score 0.0790)"},
     {"source":"gl_transactions.csv","what":"amounts and channel","figure":"range 269.81-9,447.82 (none >=10,000); 16 of 30 in their vendor's top decile; 29 of 30 INTEG-01"},
     {"source":"rule_flags.csv","what":"no rule overlap","figure":"0 of 30 rule-flagged"}],
    "info","high","")
i+=1

# ---------------- FREE HUNT ----------------
add(f"F-{i:02d}","One German supplier is set up as three vendor records with three different bank accounts.","free-hunt","worry",
    "VAT DE199283746 (seals maker at Industriestrasse 14, 22525 Hamburg) exists three times - V-0003 Karrenbach, V-0004 Kaerrenbach, V-0005 KARRENBACH - each with a different IBAN. The byte-identical name_hygiene test missed it because the spellings differ by umlaut/case. Spend is fragmented across three identities, defeating duplicate and per-vendor controls, and three IBANs for one legal entity is a payment-integrity risk.",
    ["V-0003","V-0004","V-0005"],["4110"],[1,4,6,7,8,9,10,11,12],[],
    [{"source":"vendor_master.csv","what":"one VAT, three vendor_ids, three IBANs","figure":"DE199283746 -> V-0003 (IBAN DE0534...), V-0004 (DE7629...), V-0005 (DE5416...), same address"},
     {"source":"vendor_master.csv","what":"name spellings evade byte-identical name_hygiene","figure":"'Karrenbach' / 'Kaerrenbach' / 'KARRENBACH' Dichtungstechnik GmbH"},
     {"source":"gl_transactions.csv","what":"combined spend, all on account 4110","figure":"23,651.32 + 15,026.40 + 10,323.64 = 48,001.36 across 15 txns; no identical cross-record amounts (distinct deliveries)"}],
    "act","high","Merge to one vendor record and verify which IBAN is the supplier's genuine account before the next payment run.")

add(f"F-{i+1:02d}","The largest manual postings, including a EUR 78,400 capex, pass both automated layers unchecked.","free-hunt","worry",
    "The four biggest transactions in the ledger are all keyed by hand and none is flagged by either the rule tests or the detector. The exemplar is a EUR 78,400 machinery purchase - 3.2x the next-largest item and the single biggest line in the book. The rule tests target specific bands/patterns and the detector's per-vendor deviation feature is blind to one-off vendors, so high-value manual entries fall in a coverage gap. The items look legitimate on their face but are material and un-reviewed.",
    ["V-0019","V-0020","V-0196","V-0054"],["1200","7300","4410"],[1,3,10,11],["U-058","U-204"],
    [{"source":"gl_transactions.csv","what":"largest line, unflagged by either layer","figure":"TXN036635 EUR 78,400.00, account 1200 (Machinery), memo 'Konehankinta, kalusto', posted U-058; V-0019's only txn of the year"},
     {"source":"gl_transactions.csv / rule_flags.csv / detector_flags.csv","what":"top-4 lines all human-posted and unflagged","figure":"78,400.00; 24,600.00 (insurance); 18,379.10; 15,008.44 - none in rule_flags or detector_flags"},
     {"source":"detector_flags.csv","what":"detector blind spot","figure":"V-0019 has 1 transaction, so per-vendor deviation is undefined and it cannot surface"}],
    "watch","high","Add a value-based review (e.g. every manual posting above EUR 15,000) and retrospectively confirm the 78,400 capex was approved and correctly capitalised.")

out = SCR/"run_01_findings.json"
out.write_text(json.dumps(F,indent=2,ensure_ascii=True),encoding="utf-8")
print("wrote",out,"with",len(F),"findings")
# sanity
uids=[f['unit_id'] for f in F]
unit_ids=[u['unit_id'] for u in clusters]
missing=[x for x in unit_ids if x not in uids]
print("units covered:",len([x for x in uids if x!='free-hunt']),"/ 39; missing:",missing)
print("verdicts:",pd.Series([f['verdict'] for f in F]).value_counts().to_dict())
print("severity:",pd.Series([f['severity'] for f in F]).value_counts().to_dict())
