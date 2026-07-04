"""
subscription-churn-predictor-skill: Client SDK
Predict subscription churn risk and generate targeted retention offers.
"""
from __future__ import annotations
import math
from typing import Optional

CHURN_SIGNAL_WEIGHTS = {
    "failed_payments":    30,
    "low_engagement":     20,
    "skipped_months":     18,
    "no_recent_login":    15,
    "support_friction":   12,
    "plan_downgrade":     10,
    "low_email_opens":     8,
    "new_subscriber":      5,
    "low_order_activity": 12,
}

RETENTION_OFFERS = {
    "imminent": [
        "Pause subscription for 1-2 months instead of cancelling -- no commitment required.",
        "Offer a {discount}% loyalty discount locked in for the next 6 months.",
        "Upgrade to a premium tier for free for 3 months to demonstrate value.",
        "Personal account manager call: understand the issue and offer a tailored solution.",
        "Provide an immediate refund for the most recent charge to rebuild trust.",
    ],
    "high": [
        "Send a personalized 're-engagement' box: curated products based on their history.",
        "Offer a skip-month with a 'we will make it worth your while' bonus next month.",
        "Provide a {discount}% discount on next month with a value highlight email.",
        "Invite to an exclusive members-only event or product preview.",
    ],
    "medium": [
        "Send a 'here is what you are missing' email showcasing recent additions.",
        "Offer a referral bonus: give a friend {discount}% off and receive a free item.",
        "Gamify engagement: bonus points for logging in and reviewing products this month.",
        "Feature the subscriber in a newsletter highlight as a valued community member.",
    ],
    "low": [
        "Standard monthly value reminder email with curated product picks.",
        "Ask for product feedback to increase engagement and sense of ownership.",
    ],
}


class ChurnPredictorClient:
    """
    SDK for subscription churn risk prediction and retention offer generation.
    """

    def predict(
        self,
        subscriber: dict,
        engagement: Optional[dict] = None,
        billing: Optional[dict] = None,
    ) -> dict:
        """
        Predict subscription churn risk.

        Args:
            subscriber: Core subscriber data:
                        - subscription_months (int)
                        - last_login_days (int)
                        - orders_last_90d (int)
                        - support_tickets (int)
                        - plan_tier (str: basic/standard/premium)
            engagement: Engagement signals:
                        - email_open_rate (float 0-1)
                        - portal_logins_last_30d (int)
                        - skipped_months (int)
                        - product_reviews_given (int)
            billing:    Billing signals:
                        - failed_payments_last_3m (int)
                        - plan_downgrades (int)
                        - avg_monthly_spend (float)

        Returns:
            dict with churn_risk_score, churn_probability, risk_tier, churn_drivers, retention_offers
        """
        eng = engagement or {}
        bill = billing or {}

        risk_score = 0.0
        drivers = []

        # Failed payments (biggest churn signal)
        failed = int(bill.get("failed_payments_last_3m", 0))
        if failed > 0:
            contrib = min(failed * 15, CHURN_SIGNAL_WEIGHTS["failed_payments"])
            risk_score += contrib
            drivers.append({"driver": "failed_payments", "score": round(contrib), "detail": f"{failed} failed payment(s) in last 3 months"})

        # Engagement: email open rate
        open_rate = float(eng.get("email_open_rate", 0.3))
        if open_rate < 0.15:
            contrib = CHURN_SIGNAL_WEIGHTS["low_email_opens"] * (1 - open_rate / 0.15)
            risk_score += contrib
            drivers.append({"driver": "low_email_opens", "score": round(contrib, 1), "detail": f"Email open rate: {open_rate*100:.0f}% (low)"})

        # Portal logins
        logins = int(eng.get("portal_logins_last_30d", 3))
        if logins == 0:
            contrib = CHURN_SIGNAL_WEIGHTS["no_recent_login"]
            risk_score += contrib
            drivers.append({"driver": "no_recent_login", "score": contrib, "detail": "No portal login in last 30 days"})
        elif logins < 2:
            contrib = CHURN_SIGNAL_WEIGHTS["no_recent_login"] * 0.5
            risk_score += contrib
            drivers.append({"driver": "low_engagement", "score": round(contrib), "detail": f"Only {logins} portal login(s) in 30 days"})

        # Skipped months
        skipped = int(eng.get("skipped_months", 0))
        if skipped > 0:
            contrib = min(skipped * 9, CHURN_SIGNAL_WEIGHTS["skipped_months"])
            risk_score += contrib
            drivers.append({"driver": "skipped_months", "score": round(contrib), "detail": f"{skipped} skip(s) in recent months"})

        # Support tickets
        tickets = int(subscriber.get("support_tickets", 0))
        if tickets > 2:
            contrib = min((tickets - 2) * 4, CHURN_SIGNAL_WEIGHTS["support_friction"])
            risk_score += contrib
            drivers.append({"driver": "support_friction", "score": round(contrib), "detail": f"{tickets} support tickets raised"})

        # Plan downgrade
        downgrades = int(bill.get("plan_downgrades", 0))
        if downgrades > 0:
            contrib = CHURN_SIGNAL_WEIGHTS["plan_downgrade"]
            risk_score += contrib
            drivers.append({"driver": "plan_downgrade", "score": contrib, "detail": f"{downgrades} plan downgrade(s)"})

        # Order activity
        orders_90 = int(subscriber.get("orders_last_90d", 3))
        if orders_90 == 0:
            contrib = CHURN_SIGNAL_WEIGHTS["low_order_activity"]
            risk_score += contrib
            drivers.append({"driver": "low_order_activity", "score": contrib, "detail": "No orders placed in last 90 days"})

        # New subscriber (higher natural churn in first 3 months)
        months = int(subscriber.get("subscription_months", 12))
        if months <= 3:
            contrib = CHURN_SIGNAL_WEIGHTS["new_subscriber"]
            risk_score += contrib
            drivers.append({"driver": "new_subscriber", "score": contrib, "detail": f"Only {months} month(s) as subscriber"})

        risk_score = round(min(risk_score, 100.0), 1)

        # Churn probability (sigmoid-based)
        churn_prob = round(1 / (1 + math.exp(-(risk_score - 50) / 15)), 3)

        if risk_score >= 75: tier = "imminent"
        elif risk_score >= 50: tier = "high"
        elif risk_score >= 25: tier = "medium"
        else: tier = "low"

        drivers.sort(key=lambda x: x["score"], reverse=True)

        # Build retention offers with dynamic discount
        plan = str(subscriber.get("plan_tier", "standard")).lower()
        discount = 30 if tier == "imminent" else 20 if tier == "high" else 10
        offers = [o.format(discount=discount) for o in RETENTION_OFFERS.get(tier, RETENTION_OFFERS["low"])[:3]]

        return {
            "churn_risk_score": risk_score,
            "churn_probability": churn_prob,
            "risk_tier": tier,
            "subscription_months": months,
            "plan_tier": plan,
            "churn_drivers": drivers[:5],
            "retention_offers": offers,
            "recommended_discount": discount,
        }

    def batch_predict(self, subscribers: list[dict]) -> list[dict]:
        results = []
        for s in subscribers:
            r = self.predict(
                subscriber=s.get("subscriber", {}),
                engagement=s.get("engagement", {}),
                billing=s.get("billing", {}),
            )
            r["subscriber_id"] = s.get("subscriber_id", "unknown")
            results.append(r)
        results.sort(key=lambda x: x["churn_risk_score"], reverse=True)
        return results
