# Hybrid Churn Intelligence -- Fusion & Evaluation Report

Combines the classical ML risk score (`ml_risk_score`, out-of-fold, see `data/model/ml_report.md`) and the LLM agent's text risk score (`text_risk_score`, see `data/agent/`) into a single explainable fusion model, then evaluates all three approaches -- ML-only, text-only, combined -- against the held-out `answer_key.csv`. The answer key is evaluation-only and never touches model training.

## 1. Head-to-head evaluation

| Approach | AUC | Average precision | Recall@50 | Recall@100 |
|---|---|---|---|---|
| ML-only | 0.8666 | 0.7774 | 0.3534 | 0.594 |
| Text-only | 0.7952 | 0.7051 | 0.3308 | 0.594 |
| Combined | 0.8902 | 0.8446 | 0.3684 | 0.6617 |

## 2. Per-archetype top-100 share

Share of each archetype's accounts landing in that approach's top-100.

| Archetype | N accounts | ML top-100 share | Text top-100 share | Combined top-100 share |
|---|---|---|---|---|
| A1 | 176 | 5.7% | 0.6% | 3.4% |
| A2 | 46 | 10.9% | 0.0% | 0.0% |
| A3 | 57 | 89.5% | 77.2% | 86.0% |
| A4 | 46 | 50.0% | 76.1% | 80.4% |
| A5 | 30 | 16.7% | 0.0% | 6.7% |
| A6 | 52 | 0.0% | 0.0% | 0.0% |
| A7 | 55 | 3.6% | 36.4% | 5.5% |
| A8 | 38 | 10.5% | 0.0% | 7.9% |

## 3. The 2x2 centrepiece

`ml_flag` = 1 if in ML top-100 by `ml_risk_score`; `text_flag` = 1 if in text top-100 by `text_risk_score`.

| Cell | Total accounts | True churners | Archetype breakdown |
|---|---|---|---|
| Both (ml_flag=1, text_flag=1) | 58 | 57 | A3=40, A4=17, A7=1 |
| ML only (1,0) | 42 | 22 | A1=10, A2=5, A3=11, A4=6, A5=5, A7=1, A8=4 |
| Text only (0,1) | 42 | 22 | A1=1, A3=4, A4=18, A7=19 |
| Neither (0,0) | 358 | 32 | A1=165, A2=41, A3=2, A4=5, A5=25, A6=52, A7=34, A8=34 |

### The A7 verdict

A7 ('loud but loyal') is designed to NEVER churn and the agent must NOT flag it -- angry tickets that always resolve fast are not a risk signal. Of the 55 A7 accounts (mean text_risk_score 0.489), **20 (36.4%) land in the text top-100** -- the agent layer's honest false-positive rate on this archetype. Of those, fusion rescues **19** out of the combined top-100 (the ML signal and other fusion features outweigh the text score), while **1** still remains flagged in the combined top-100.

### The A5 honesty check

A5 ('sudden death') is designed to be undetectable by either layer -- no usage decline, no text signal, the churn driver is exogenous (acquisitions, budget cuts, champion leaves). Of 30 A5 accounts: **5** in ML top-100, **0** in text top-100, **2** in combined top-100. Low, near-baseline counts here are the expected, honest result -- not a failure of either layer.

## 4. The A4 table (the money segment)

A4 ('quietly unhappy') is designed to be near-invisible to the classical model and caught by the agent reading ticket text. Of 46 A4 accounts:

| Approach | N of 46 A4 accounts in top-100 |
|---|---|
| ML top-100 | 23 |
| Text top-100 | 35 |
| Combined top-100 | 37 |

**Headline delta: text top-100 vs ML top-100 = +12 accounts. Combined top-100 vs ML top-100 = +14 accounts.**

## 5. Fusion model coefficients

Logistic regression fit once on the full 500-account dataset for explainability (the reported combined_score itself comes from out-of-fold predictions, not this full fit).

| Feature | Raw coefficient | Standardized coefficient |
|---|---|---|
| ml_risk_score | 3.4088 | 1.3166 |
| text_risk_score | 1.2902 | 0.5261 |
| trajectory_ordinal | 1.2021 | 0.6839 |
| n_serious_competitor_mentions | 0.8263 | 0.336 |
| escalation_pattern | -0.0888 | -0.162 |
| intercept | -2.8089 | -1.522 |

Raw coefficients are on each feature's native scale (not comparable to each other). Standardized coefficients (features scaled to zero mean / unit variance before fitting) are comparable in magnitude -- the largest standardized coefficient is the strongest driver of the fusion model's risk score.

## 6. Business translation (ARR-weighted)

Total ARR of all churned accounts: **EUR 6,529,635**.

### ARR caught at top-100

| Approach | ARR caught (churned accounts in top-100) |
|---|---|
| ML-only | EUR 3,711,649 |
| Text-only | EUR 4,349,027 |
| Combined | EUR 4,571,080 |

**Incremental ARR text uniquely surfaces (churned, in text top-100 but not ML top-100): EUR 1,340,728.**
Incremental ARR ML uniquely surfaces (churned, in ML top-100 but not text top-100): EUR 703,350.

### Review budget framing (top-50 instead of top-100)

| Approach | Churners caught (top-50) | ARR caught (top-50) |
|---|---|---|
| ML-only | 47 | EUR 2,280,168 |
| Text-only | 44 | EUR 2,744,860 |
| Combined | 49 | EUR 2,593,838 |

## 7. Segmentation of the combined top-100

**Rule:** worth-saving = arr_eur above the combined top-100 median (EUR 37,026) AND (frustration_trajectory == 'deteriorating' OR n_serious_competitor_mentions > 0); everything else in the combined top-100 is low-leverage.

| Segment | N accounts | Total ARR |
|---|---|---|
| Worth-saving | 46 | EUR 3,831,253 |
| Low-leverage | 54 | EUR 1,296,425 |
