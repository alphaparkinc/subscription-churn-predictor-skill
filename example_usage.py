"""
example_usage.py -- Demonstrates the ChurnPredictorClient SDK.
"""
from client import ChurnPredictorClient

def main():
    client = ChurnPredictorClient()

    print("[1] High-Risk Subscriber Churn Prediction")
    result = client.predict(
        subscriber={"subscription_months": 4, "orders_last_90d": 0, "support_tickets": 4, "plan_tier": "standard"},
        engagement={"email_open_rate": 0.08, "portal_logins_last_30d": 0, "skipped_months": 2},
        billing={"failed_payments_last_3m": 1, "plan_downgrades": 1, "avg_monthly_spend": 29.99},
    )
    print(f"Churn Risk Score:   {result['churn_risk_score']}/100")
    print(f"Churn Probability:  {result['churn_probability']*100:.1f}%")
    print(f"Risk Tier:          {result['risk_tier'].upper()}")
    print(f"Recommended Discount: {result['recommended_discount']}%")
    print(f"\nChurn Drivers:")
    for d in result["churn_drivers"]:
        print(f"  [{d['score']}pts] {d['driver']}: {d['detail']}")
    print(f"\nRetention Offers:")
    for offer in result["retention_offers"]:
        print(f"  -> {offer}")

    print("\n[2] Batch Churn Scoring")
    subscribers = [
        {"subscriber_id":"S001","subscriber":{"subscription_months":2,"orders_last_90d":0,"support_tickets":3},"engagement":{"email_open_rate":0.05,"portal_logins_last_30d":0,"skipped_months":2},"billing":{"failed_payments_last_3m":2}},
        {"subscriber_id":"S002","subscriber":{"subscription_months":18,"orders_last_90d":6,"support_tickets":0},"engagement":{"email_open_rate":0.45,"portal_logins_last_30d":8,"skipped_months":0},"billing":{"failed_payments_last_3m":0}},
        {"subscriber_id":"S003","subscriber":{"subscription_months":7,"orders_last_90d":2,"support_tickets":1},"engagement":{"email_open_rate":0.20,"portal_logins_last_30d":2,"skipped_months":1},"billing":{"failed_payments_last_3m":0}},
    ]
    batch = client.batch_predict(subscribers)
    print(f"{'ID':<8} {'Risk Score':>12} {'Probability':>13} {'Tier':>10}")
    for s in batch:
        print(f"{s['subscriber_id']:<8} {s['churn_risk_score']:>12.1f} {s['churn_probability']*100:>12.1f}% {s['risk_tier'].upper():>10}")

if __name__ == "__main__":
    main()
