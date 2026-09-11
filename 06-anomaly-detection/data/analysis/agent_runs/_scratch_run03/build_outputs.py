# -*- coding: utf-8 -*-
import json
from pathlib import Path
OUT = Path(r"C:\Users\luigi\Dropbox\Archivio famiglia\Hapax\Case Studies\06 Anomaly Detection\data\analysis\agent_runs\_scratch_run03")

def ev(src, what, fig): return {"source": src, "what": what, "figure": fig}
F=[]

# ---------- RULE UNITS ----------
F.append({
 "finding_id":"F-01","headline":"Marketing agency's campaign invoices are all booked to IT services instead of Marketing.",
 "unit_id":"RU-01","verdict":"worry",
 "mechanism":"Consistent expense misclassification. Every invoice from the advertising agency V-0006 (memo 'Mainoskampanja' = advertising campaign) is posted to 7200 IT services by AP user U-204, although the vendor's only allowed account is 7100 Marketing. Spend is landing in the wrong cost line, understating Marketing and inflating IT.",
 "affected":{"vendor_ids":["V-0006"],"accounts":["7200","7100"],"months":[9,10],"users":["U-204"]},
 "evidence":[ev("gl_transactions.csv","all V-0006 rows: account used vs allowed","8/8 rows on 7200; vendor_master allowed_accounts=7100 only"),
   ev("gl_transactions.csv","memos and amount misallocated","all say 'Mainoskampanja, syys/lokakuu 2025'; EUR 36,934.24 total"),
   ev("gl_transactions.csv","peers book Marketing correctly","5 vendors post to 7100; V-0006 never does")],
 "severity":"watch","confidence":"high",
 "recommended_action":"Reclassify the 8 invoices (EUR 36,934) from 7200 to 7100 and fix the default account behind U-204's postings for this vendor."})

def dup(fid,unit,vid,pairs,total_over,conf):
    return {"finding_id":fid,"headline":f"Same purchase order billed twice at an identical amount ({vid}).",
     "unit_id":unit,"verdict":"worry",
     "mechanism":"Potential duplicate payment. Each order number appears on two different invoice numbers a few days apart for the identical amount to the cent, with plain 'Ostolasku' memos (no partial-delivery wording). Nothing in the data distinguishes the second invoice from a re-bill of the first.",
     "affected":{"vendor_ids":[vid],"accounts":[],"months":[],"users":["INTEG-01"]},
     "evidence":[ev("gl_transactions.csv","matched order (tilaus) billed twice, identical amount",pairs),
       ev("gl_transactions.csv","the whole vendor history is these paired invoices","4 txns, 2 order numbers, 2 invoices each"),
       ev("gl_transactions.csv","overpayment exposure if confirmed duplicate",total_over)],
     "severity":"watch","confidence":conf,
     "recommended_action":"AP to confirm the second invoice on each order is not a re-bill of the first; recover if duplicated."}
F.append(dup("F-02","RU-02","V-0008","order 358022 -> inv 801524 & 801525 both EUR 842.50 (4d); order 358023 -> inv 801526 & 801527 both EUR 615.20 (7d)","EUR 1,457.70","medium"))
F.append(dup("F-03","RU-03","V-0009","order 787675 -> inv 930804 & 930805 both EUR 1,365.00 (5d); order 787676 -> inv 930806 & 930807 both EUR 3,780.60 (5d)","EUR 5,145.60","medium"))
F.append(dup("F-04","RU-04","V-0010","order 847310 -> inv 716170 & 716171 both EUR 2,940.75 (6d); order 847311 -> inv 716172 & 716173 both EUR 1,120.35 (6d)","EUR 4,061.10","medium"))

F.append({
 "finding_id":"F-05","headline":"Steel supplier billed in exact round thousands every two months.",
 "unit_id":"RU-05","verdict":"worry",
 "mechanism":"Round-number billing atypical for weight-priced steel. Six invoices are each an exact EUR 1,000 multiple (5,000/6,000/7,000/8,000/9,000/6,000) on a fixed bi-monthly cadence. Steel priced by weight normally yields odd cents; exact thousands point to fixed-fee or estimated billing that should be tied to a contract. No threshold is approached and nothing is split, so the risk is only that amounts may be estimates rather than actuals.",
 "affected":{"vendor_ids":["V-0011"],"accounts":["4100"],"months":[1,3,5,7,9,11],"users":["INTEG-01"]},
 "evidence":[ev("gl_transactions.csv","six exact-thousand invoices, consecutive orders 077948-077953","EUR 41,000 total; all multiples of 1000"),
   ev("rule_flags.csv","round-thousand invoices are rare ledger-wide","only 18 round_sum rows exist, from just 2 vendors (this + rent)"),
   ev("gl_transactions.csv","no threshold proximity","max invoice 9,000, below the 9,500 near-threshold band")],
 "severity":"watch","confidence":"low",
 "recommended_action":"Spot-check the V-0011 supply agreement to confirm these are contracted fixed fees and not round-number estimates."})

F.append({
 "finding_id":"F-06","headline":"Freight vendor's invoices sit just under the EUR 10,000 approval limit every quarter.",
 "unit_id":"RU-06","verdict":"worry",
 "mechanism":"Threshold structuring. All four freight invoices land in EUR 9,580-9,899.99 - within EUR 420 of the EUR 10,000 department-head approval tier - on a regular quarterly cadence, and never cross it. This is the classic signature of pricing kept deliberately below an approval limit.",
 "affected":{"vendor_ids":["V-0012"],"accounts":["4410"],"months":[2,5,8,11],"users":["INTEG-01"]},
 "evidence":[ev("gl_transactions.csv","all four invoice amounts","9,580.10 / 9,650.75 / 9,712.45 / 9,899.99 (mean 9,710.82)"),
   ev("gl_transactions.csv","only vendor in the whole ledger in the 9,500-9,999.99 band","4 of 4 near-threshold rows are V-0012; no other vendor"),
   ev("gl_transactions.csv","51 other invoices openly exceed 10,000","so large invoices are normally allowed to cross - V-0012 never does")],
 "severity":"act","confidence":"medium",
 "recommended_action":"Put these freight charges through department-head review regardless of amount and ask the buyer/vendor why they cluster just under EUR 10,000."})

def split(fid,unit,vid,pairs,acct,months):
    return {"finding_id":fid,"headline":f"Two sub-threshold invoices a day or two apart sum to over EUR 10,000 ({vid}).",
     "unit_id":unit,"verdict":"worry",
     "mechanism":"Possible split to avoid the EUR 10,000 department-head approval. Each pair is two invoices of EUR 4,000-7,500 posted 1-3 days apart on consecutive order numbers, together exceeding EUR 10,000, same account. Memos say 'osatoimitus' (partial delivery), which is the benign alternative; but the consecutive-PO, sub-threshold, tight-timing pattern is the structuring signature.",
     "affected":{"vendor_ids":[vid],"accounts":[acct],"months":months,"users":["INTEG-01"]},
     "evidence":[ev("gl_transactions.csv","paired parts and their sums",pairs),
       ev("gl_transactions.csv","only three vendors in the whole ledger show this pattern","split sweep returns 5 pairs, all from V-0013/V-0014/V-0015"),
       ev("gl_transactions.csv","the entire vendor history is these sub-threshold pairs","vendor never issues a single invoice above the parts")],
     "severity":"watch","confidence":"medium",
     "recommended_action":"Confirm whether each pair stems from one procurement that should have carried department-head approval; if so, require approval and review the buyer."}
F.append(split("F-07","RU-07","V-0013","5,820.40+5,495.10=11,315.50 (2d, orders 238987/238988); 6,340.25+6,910.80=13,251.05 (1d, 238989/238990)","4110",[1,7]))
F.append(split("F-08","RU-08","V-0014","4,780.60+6,255.90=11,036.50 (3d, orders 732301/732302); 7,120.15+4,610.35=11,730.50 (2d, 732303/732304)","4310",[4,10]))
F.append(split("F-09","RU-09","V-0015","5,990.55+7,340.20=13,330.75 (1d, orders 890739/890740)","4420",[9]))

F.append({
 "finding_id":"F-10","headline":"Monthly premises rent of exactly EUR 15,000 - a normal round recurring charge.",
 "unit_id":"RU-10","verdict":"stand_down",
 "mechanism":"Benign. Twelve identical EUR 15,000 invoices, one per calendar month, on account 7000 Premises rent, consecutive invoice numbers. Rent is legitimately a fixed round monthly amount; the round_sum test fires on it mechanically.",
 "affected":{"vendor_ids":["V-0016"],"accounts":["7000"],"months":[1,2,3,4,5,6,7,8,9,10,11,12],"users":["INTEG-01"]},
 "evidence":[ev("gl_transactions.csv","12 rent invoices","each EUR 15,000, monthly, invno 674843-674854, memo 'Toimitilavuokra'"),
   ev("vendor_master.csv","account matches vendor purpose","V-0016 is Kiinteisto Oy (property company); allowed_accounts=7000")],
 "severity":"info","confidence":"high","recommended_action":""})

F.append({
 "finding_id":"F-11","headline":"Same amount (EUR 7,420.00) billed twice within four days on two different PO numbers.",
 "unit_id":"RU-11","verdict":"worry",
 "mechanism":"Possible duplicate. Two invoices of exactly EUR 7,420.00 four days apart, consecutive invoice numbers, but different PO references (PO-48213 vs PO-48297). Different POs make a genuine repeat order plausible, so this is weaker than the same-order duplicates - but an identical to-the-cent amount warrants a check.",
 "affected":{"vendor_ids":["V-0018"],"accounts":["4200"],"months":[6],"users":["INTEG-01"]},
 "evidence":[ev("gl_transactions.csv","the pair","TXN021299 & TXN022042, both EUR 7,420.00, 4 days apart, inv 005784/005785, PO-48213 vs PO-48297"),
   ev("gl_transactions.csv","whole vendor history","only these 2 txns exist for V-0018")],
 "severity":"watch","confidence":"low",
 "recommended_action":"AP to confirm two separate deliveries were received against the two POs before treating as distinct."})

F.append({
 "finding_id":"F-12","headline":"Weekend postings are a documented agreed stocktake - benign.",
 "unit_id":"RU-12","verdict":"stand_down",
 "mechanism":"Benign. Both invoices were posted by U-031 on Saturday 15 Nov and the memos themselves state the reason: 'Sovittu ylityo, inventaario 15.11.2025' (agreed overtime, stocktake 15 Nov). The calendar test fires on the non-working-day posting; the business reason is on the line.",
 "affected":{"vendor_ids":["V-0017"],"accounts":["4420"],"months":[11],"users":["U-031"]},
 "evidence":[ev("gl_transactions.csv","both memos","'Sovittu ylityo, inventaario 15.11.2025'; amounts EUR 1,260.80 and 1,840.35"),
   ev("company_calendar.csv","2025-11-15 is a weekend","is_working_day=False")],
 "severity":"info","confidence":"high","recommended_action":""})

F.append({
 "finding_id":"F-13","headline":"U-117 is the only AP user who posts on weekends, with no stated reason (8 times).",
 "unit_id":"RU-13","verdict":"worry",
 "mechanism":"Control observation, most likely benign. U-117 made 8 non-working-day postings across Feb-Jun; the invoices are small, diverse in vendor and account, and all within allowed mappings. The only signal is that no other AP user posts on weekends at all - so it is worth one confirmation that U-117's weekend access is authorised.",
 "affected":{"vendor_ids":[],"accounts":["4200","7850","4210","4000","4420","7200"],"months":[2,3,4,5,6],"users":["U-117"]},
 "evidence":[ev("gl_transactions.csv","U-117 weekend posts vs total","8 weekend rows out of 1,466; EUR 7,504.66; amounts EUR 300-2,000"),
   ev("gl_transactions.csv","peer contrast","U-058/U-204/U-142/U-176 each ~1,450 posts, 0 on weekends"),
   ev("gl_transactions.csv","no explanatory memos (unlike U-031)","memos are routine 'Tavarantoimitus/Ostolasku'")],
 "severity":"watch","confidence":"low",
 "recommended_action":"Confirm U-117 is authorised to post on non-working days; otherwise route weekend work through the standard channel."})

# ---------- DETECTOR VENDOR UNITS (all stand_down) ----------
def du(fid,unit,vid,nfl,accts,fmax,vmax,vmed,driver,months,extra_ev=None,note="",sev="info",users=None):
    e=[ev("detector_flags.csv","flagged count / top score for vendor",f"{nfl} flags, all in the detector's statistical tail"),
       ev("gl_transactions.csv","flagged amounts vs vendor's own range",f"flagged max EUR {fmax} within vendor min..max (max EUR {vmax}, median EUR {vmed})"),
       ev("vendor_master.csv","accounts used are all allowed",f"accounts {accts} all in allowed_accounts; no mapping/duplicate/threshold rule fired")]
    if extra_ev: e.append(extra_ev)
    return {"finding_id":fid,"unit_id":unit,"verdict":"stand_down",
     "headline":f"{vid}: detector flags are the vendor's large/rare-but-in-range invoices - benign tail."+((" "+note) if note else ""),
     "mechanism":"Benign statistical tail. "+driver+" No rule test fired on any of these lines; amounts sit inside the vendor's own history and accounts are all allowed. This is the Isolation Forest surfacing the upper/rarer end of a normal vendor's distribution.",
     "affected":{"vendor_ids":[vid],"accounts":accts,"months":months,"users":users or ["INTEG-01"]},
     "evidence":e,"severity":sev,"confidence":"high","recommended_action":""}

F.append(du("F-14","DU-01","V-0029",7,["4020","4200"],"1,560.35","2,918.05","570.31","5 of 7 fall in December (year-end cadence) plus the rarer 4020 packaging account.",[4,7,12],users=["INTEG-01","U-058"]))
F.append(du("F-15","DU-02","V-0037",6,["7400","7900"],"2,571.01","2,571.01","824.17","The flagged rows are simply this vendor's largest invoices on its two normal accounts.",[3,5,7,9,11]))
F.append(du("F-16","DU-03","V-0041",5,["4300"],"1,264.99","2,586.27","567.28","All five are on account 4300 and posted on non-working days by INTEG-01 (exempt); amounts are mid-range.",[1,9,10,11]))
F.append(du("F-17","DU-04","V-0062",3,["7100","7900"],"2,865.74","3,994.29","909.90","Three larger invoices on the vendor's two allowed accounts.",[1,3,8],users=["INTEG-01","U-058"]))
F.append(du("F-18","DU-05","V-0067",7,["7850","7990"],"2,956.57","3,373.29","797.40","The vendor's larger invoices across its two allowed accounts; nothing crosses a threshold.",[1,2,6,10,12]))
F.append(du("F-19","DU-06","V-0072",3,["4000"],"487.38","2,338.38","560.12","Flagged for account rarity, not size: three small invoices on 4000, the vendor's less-used allowed account (mostly 4300).",[4,8,11]))
F.append(du("F-20","DU-07","V-0076",4,["4420","4440"],"5,353.57","5,828.69","1,651.24","A high-volume vendor (664 txns, EUR 1.24M); the flags are its larger invoices plus the rarer 4440 account.",[1,6,11]))
F.append(du("F-21","DU-08","V-0078",14,["4010","4310"],"6,172.62","6,588.79","3,155.93","An active mid-size vendor (160 txns, EUR 0.52M) with consistently large invoices; 14 land in the tail.",[1,2,3,4,6,7,8,10,11,12],
   extra_ev=ev("gl_transactions.csv","semantic aside, not a rule breach","FI vendor books some lines to 4010 Foreign purchases, but 4010 is in its allowed_accounts"),
   note="(FI vendor using foreign-purchases account 4010 is odd but allowed.)",users=["INTEG-01","U-204","U-058"]))
F.append(du("F-22","DU-09","V-0090",9,["4200","4300"],"1,790.95","3,757.68","580.78","All nine are weekend INTEG-01 postings (exempt) with mid-range amounts; timing drives the score.",[1,2,3,4,5,7,8,9,10]))
F.append(du("F-23","DU-10","V-0098",4,["4020","4300"],"2,007.60","2,098.26","601.52","Four larger invoices incl. the vendor's near-max; both accounts allowed.",[1,2,3,5]))
F.append(du("F-24","DU-11","V-0099",11,["4410","4440"],"11,281.91","11,281.91","1,862.69","Includes the vendor's genuine maximum (EUR 11,281.91 freight/services); the rest are its larger invoices. Openly large, not split or near a threshold.",[1,2,3,6,9,10,11]))
F.append(du("F-25","DU-12","V-0110",3,["4000","4210"],"2,268.31","2,268.31","527.41","Three larger invoices including the vendor's maximum.",[5,9,10]))
F.append(du("F-26","DU-13","V-0114",7,["7200","7250"],"1,377.82","3,403.77","806.63","IT/software vendor; flags are mid-to-large invoices on its two allowed accounts.",[3,4,5,7,11,12]))
F.append(du("F-27","DU-14","V-0118",6,["4000","4200"],"769.74","2,226.87","597.53","Small invoices flagged on account/timing rarity, not amount.",[3,5,8,10,12],users=["INTEG-01","U-142"]))
F.append(du("F-28","DU-15","V-0121",6,["7990"],"2,351.65","4,588.56","801.25","All six on 7990 (a catch-all allowed account); amounts mid-range, well below the vendor's max.",[1,3,5,9,12]))
F.append(du("F-29","DU-16","V-0125",5,["7400"],"2,119.78","3,489.70","776.97","Five larger telecom invoices; account allowed.",[2,3,5,6,10]))
F.append(du("F-30","DU-17","V-0131",17,["4110","4310"],"6,938.75","7,066.54","3,121.44","A large seals/components vendor (166 txns, EUR 0.54M) with big invoices throughout; 17 populate the tail, all in-range and account-compliant.",[1,2,3,4,6,7,9,10,11,12],users=["INTEG-01","U-117"]))
F.append(du("F-31","DU-18","V-0132",3,["4310"],"10,039.71","10,039.71","2,944.39","The vendor's three largest single invoices, incl. its maximum EUR 10,039.71 - a single line, not a split.",[2,6,8],
   extra_ev=ev("gl_transactions.csv","one line exceeds the 10k tier openly","EUR 10,039.71 single invoice - confirm it carried department-head approval (routine for the 51 over-10k invoices)"),
   note="(One invoice EUR 10,039.71 openly exceeds the 10k approval tier.)"))
F.append(du("F-32","DU-19","V-0135",9,["7200","7400"],"3,721.96","4,091.51","775.38","Contains the ledger's top-ranked anomaly (TXN024115, EUR 3,721.96) - large only relative to this vendor's low median (EUR 775); high per-vendor deviation, not an amount or control breach.",[1,3,4,7,9,11,12]))
F.append(du("F-33","DU-20","V-0155",3,["7100"],"1,943.29","5,141.54","809.99","Three marketing invoices, two posted 24 Dec (year-end); amounts modest.",[4,12]))
F.append(du("F-34","DU-21","V-0156",8,["4020","4200"],"811.49","2,197.98","552.11","Eight small invoices flagged on account/timing rarity, not amount (all below the vendor's median-plus range).",[1,2,4,6,7,9]))
F.append(du("F-35","DU-22","V-0157",7,["4100","4310"],"6,615.30","7,832.79","2,962.12","The vendor's larger invoices on its two allowed accounts; nothing near a threshold.",[2,5,6,7,9,11]))
F.append(du("F-36","DU-23","V-0176",3,["4020","4300"],"1,246.51","3,276.52","552.90","Three mid-range invoices, flagged partly on the rarer 4020 account.",[3,7,10]))
F.append(du("F-37","DU-24","V-0198",10,["7250","7850"],"2,440.87","2,872.17","768.66","Ten larger invoices on the vendor's two allowed accounts; all in-range.",[1,2,3,5,7,8,9,11,12],users=["INTEG-01","U-117"]))

# ---------- SINGLES ----------
F.append({
 "finding_id":"F-38","headline":"Ten isolated top-rank anomalies, each a vendor's single large or rare invoice - benign.",
 "unit_id":"SINGLES","verdict":"stand_down",
 "mechanism":"Benign. Each of the ten is the only flag for its vendor and is that vendor's largest or a rare-account invoice - five are at or within a whisker of the vendor's maximum (V-0071 8,464.74=max; V-0195 7,575.97=max; V-0105 6,253.77 vs 6,268; V-0171 6,721.38 vs 7,267; V-0095 6,092 vs 6,954). All are single INTEG-01 lines on allowed accounts with no rule breach - the detector isolating genuine high-value one-offs, not a coordinated pattern.",
 "affected":{"vendor_ids":["V-0023","V-0071","V-0075","V-0095","V-0105","V-0142","V-0150","V-0171","V-0195"],"accounts":["4110","4430","7250","4310","7700","4300","4020"],"months":[1,2,3,7,11,12],"users":["INTEG-01"]},
 "evidence":[ev("detector_flags.csv","score range of the ten","0.0237-0.0750; these are individually high-ranked (incl. overall rank 2)"),
   ev("gl_transactions.csv","each within its vendor's range","5 of 10 equal/near the vendor max; none exceed it"),
   ev("gl_transactions.csv","two larger discretionary items worth an eyeball","EUR 7,575.97 representation (7700, V-0195) and EUR 8,464.74 consulting (4430, V-0071)")],
 "severity":"watch","confidence":"high",
 "recommended_action":"Eyeball the two larger discretionary invoices (EUR 7,576 representation and EUR 8,465 consulting) for supporting documentation; no pattern action needed."})

# ---------- RESIDUAL ----------
F.append({
 "finding_id":"F-39","headline":"The 30-line residual tail is the lowest-scoring flags - the upper-amount invoices of big vendors, all compliant.",
 "unit_id":"RESIDUAL","verdict":"stand_down",
 "mechanism":"Benign distributional tail. These are the least anomalous flagged rows (scores 0.0005-0.016, all below the SINGLES floor of 0.024). They are the larger invoices of high-volume vendors (V-0197 EUR 4.67M, V-0159, V-0162, V-0108, V-0068, V-0153, etc.), every one on an allowed account, all INTEG-01, none breaching a rule test. The Nov/Dec concentration matches the ledger's normal seasonality (year-end stocking peak, July trough).",
 "affected":{"vendor_ids":["V-0197","V-0159","V-0162","V-0108","V-0068","V-0153","V-0191","V-0085","V-0163"],"accounts":["4310","4430","4100","4010","4020","4000","7000","7700"],"months":[1,2,3,4,6,7,8,9,10,11,12],"users":["INTEG-01","U-176"]},
 "evidence":[ev("detector_flags.csv","scores are the bottom of the flagged set","0.00050-0.01603, all below every SINGLES score"),
   ev("gl_transactions.csv","amounts within vendor ranges, accounts allowed","largest is EUR 9,447.82 (V-0191, 4010, allowed); no rule test fired on any of the 30"),
   ev("gl_transactions.csv","timing matches ledger seasonality","monthly account totals peak Nov/Dec and trough in July across the whole ledger")],
 "severity":"info","confidence":"high","recommended_action":""})

# ---------- FREE HUNT ----------
F.append({
 "finding_id":"F-40","headline":"One German supplier (VAT DE199283746) is set up as three vendor records with three different bank accounts.",
 "unit_id":"free-hunt","verdict":"worry",
 "mechanism":"Vendor-master defect the automated layer could not catch. Kaerrenbach Dichtungstechnik GmbH exists three times (V-0003/V-0004/V-0005) under three spellings - 'Kaerrenbach', 'Karrenbach', 'KARRENBACH' - sharing one VAT number but carrying three different IBANs. Total spend of EUR 48,001 is fragmented across the three records, hiding the true exposure, and three payment accounts for one legal entity is a payment-diversion vector. The byte-identical name_hygiene rule missed it because the three names are not byte-identical; keying on VAT rather than name exposes it.",
 "affected":{"vendor_ids":["V-0003","V-0004","V-0005"],"accounts":["4110"],"months":[1,4,6,7,8,9,10,11,12],"users":["INTEG-01"]},
 "evidence":[ev("vendor_master.csv","one VAT, three records, three IBANs","VAT DE199283746 on V-0003/4/5; IBANs DE0534..., DE7629..., DE5416... (all different)"),
   ev("gl_transactions.csv","fragmented spend","V-0003 EUR 23,651 (7 inv) + V-0004 EUR 15,026 (5) + V-0005 EUR 10,324 (3) = EUR 48,001, all account 4110 'Tiivistetoimitus'"),
   ev("rule_flags.csv","why automation missed it","0 name_hygiene flags exist; the test requires byte-identical names, defeated by the three spellings/cases")],
 "severity":"act","confidence":"high",
 "recommended_action":"Merge the three records into one vendor and verify each IBAN belongs to the legitimate supplier before releasing further payment."})

assert len(F)==40, len(F)
(OUT/"run_03_findings.json").write_text(json.dumps(F,ensure_ascii=True,indent=2),encoding="utf-8")
print("wrote run_03_findings.json with",len(F),"findings")
from collections import Counter
print("verdicts:",Counter(x["verdict"] for x in F))
print("severity:",Counter(x["severity"] for x in F))
print("units covered:",len(set(x["unit_id"] for x in F if x["unit_id"].startswith(("RU","DU"))))+ (1 if any(x["unit_id"]=="SINGLES" for x in F) else 0)+(1 if any(x["unit_id"]=="RESIDUAL" for x in F) else 0))
