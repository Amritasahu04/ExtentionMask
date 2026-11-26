from core.signatures import (
    DANGEROUS_EXTENSIONS,
    EXTENSION_MAP
)


RISK_WEIGHTS = {
    "File extension mismatch": 40,
    "Deceptive double extension": 50,
    "Suspicious Unicode characters": 30
}


def analyze_risk(result):
    score = 0
    reasons = []

    if result["status"] == "Error":
        return {
            "risk_score": None,
            "severity": "Unknown",
            "risk_reasons": ["File analysis failed"]
        }

    threats = result.get("threats", [])
    declared = result.get("declared_extension", "")
    actual = result.get("actual_type", "Unknown")

    # Calculate points for detected threats
    for threat in threats:
        points = RISK_WEIGHTS.get(threat, 0)

        if points:
            score += points
            reasons.append(threat)

    # Check potentially dangerous extensions
    if declared in DANGEROUS_EXTENSIONS:
        score += 20
        reasons.append(
            "Potentially dangerous file extension"
        )

    # Check disguised executable files
    executable_extensions = EXTENSION_MAP.get(
        "exe", {"exe"}
    )

    if (
        actual == "exe"
        and declared not in executable_extensions
    ):
        score += 60
        reasons.append(
            "Executable disguised as another file type"
        )

    # Cap risk score at 100
    score = min(score, 100)

    # Classify threat severity
    if score >= 80:
        severity = "Critical"
    elif score >= 60:
        severity = "High"
    elif score >= 30:
        severity = "Medium"
    elif score > 0:
        severity = "Low"
    elif result["status"] == "Unverified":
        severity = "Unknown"
    else:
        severity = "None"

    return {
        "risk_score": score,
        "severity": severity,
        "risk_reasons": reasons
    }
