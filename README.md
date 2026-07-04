# subscription-churn-predictor-skill

> **GenPark AI Agent Skill** -- Predict subscription churn risk and generate targeted retention offers using engagement and billing signals.

## Features

- Multi-signal churn scoring: failed payments, email open rate, portal logins, skipped months, support tickets, plan downgrades
- Risk tiers: Imminent (75+) / High (50-74) / Medium (25-49) / Low (<25)
- Sigmoid-based churn probability estimation
- Dynamic retention offers with discount tiers (10/20/30% based on risk)
- Batch prediction for at-risk subscriber queue management
- Key churn driver identification for root-cause analysis

## Quick Start

```python
from client import ChurnPredictorClient

client = ChurnPredictorClient()
result = client.predict(
    subscriber={"subscription_months": 3, "orders_last_90d": 0, "support_tickets": 3},
    engagement={"email_open_rate": 0.05, "portal_logins_last_30d": 0, "skipped_months": 2},
    billing={"failed_payments_last_3m": 1},
)
print(f"Churn Risk: {result['churn_risk_score']}/100 ({result['risk_tier']})")
for offer in result["retention_offers"]:
    print(f"  -> {offer}")
```

## Installation

```bash
python example_usage.py  # No external dependencies
```

---
Built by [GenPark](https://genpark.ai) | [alphaparkinc](https://github.com/alphaparkinc)
