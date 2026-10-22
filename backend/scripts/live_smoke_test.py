from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi.testclient import TestClient

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPOSITORY_ROOT / ".env", override=False)

from backend.app.main import app, resolve_runtime_mode

SAMPLE_SCAM_TEXT = (
    "Urgent internship opening! We need a ₹5000 security deposit before onboarding.\n"
    "Email hr@internship-portal.xyz and contact me on WhatsApp immediately.\n"
    "Regards, Priya Sharma\n"
    "No interview needed. Submit Aadhaar and OTP."
)


def main() -> None:
    mode = resolve_runtime_mode()
    if mode != "live":
        raise SystemExit("Live mode is required; smoke test was not run.")

    try:
        with TestClient(app) as client:
            response = client.post("/api/verify", json={"text": SAMPLE_SCAM_TEXT})
        if response.status_code != 200:
            raise SystemExit("Verification failed; response details were suppressed.")
        report = response.json()
    except SystemExit:
        raise
    except Exception:
        raise SystemExit("Smoke test failed; sensitive details were suppressed.") from None

    print(f"mode: {mode}")
    print(f"risk_score: {report['risk_score']}")
    print(f"level: {report['level']}")
    for check in report["checks"]:
        print(f"{check['name']} | {check['status']} | {check['risk_points']}")


if __name__ == "__main__":
    main()