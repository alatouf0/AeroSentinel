import streamlit as st
from datetime import datetime

st.set_page_config(page_title="AeroReg Control", page_icon="🛩️", layout="wide")

st.title("🛡️AeroSentinel Control")
st.caption("Real-Time UAV Compliance, Safety & Violation Prevention System")

# -----------------------------
# Regulatory thresholds
# -----------------------------
REGULATIONS = {
    "UAE GCAA - Prototype Rules": {
        "max_altitude_m": 120,
        "max_speed_kmh": 100,
        "max_weight_kg": 25,
    },
    "FAA Part 107 - Prototype Rules": {
        "max_altitude_m": 122,
        "max_speed_kmh": 161,
        "max_weight_kg": 25,
    },
    "EASA Open Category - Prototype Rules": {
        "max_altitude_m": 120,
        "max_speed_kmh": 100,
        "max_weight_kg": 25,
    },
}

SCENARIOS = {
    "Manual Input": None,
    "Safe Educational Flight": {
        "weight": 10,
        "altitude": 60,
        "speed": 35,
        "battery": 85,
        "gps": 90,
        "communication": 95,
        "motor_temp": 45,
        "vibration": 20,
        "near_airport": False,
        "near_people": False,
        "restricted_zone": False,
    },
    "Altitude Violation": {
        "weight": 12,
        "altitude": 180,
        "speed": 60,
        "battery": 75,
        "gps": 85,
        "communication": 90,
        "motor_temp": 50,
        "vibration": 25,
        "near_airport": False,
        "near_people": False,
        "restricted_zone": False,
    },
    "High-Risk Urban Delivery": {
        "weight": 30,
        "altitude": 140,
        "speed": 120,
        "battery": 18,
        "gps": 45,
        "communication": 55,
        "motor_temp": 82,
        "vibration": 70,
        "near_airport": True,
        "near_people": True,
        "restricted_zone": True,
    },
}

def assess_compliance(data, rules):
    violations = []
    warnings = []
    prevention_actions = []

    if data["weight"] > rules["max_weight_kg"]:
        violations.append(f"Drone weight exceeds limit: {data['weight']} kg > {rules['max_weight_kg']} kg.")
        prevention_actions.append("Block takeoff or require special operational approval.")

    if data["altitude"] > rules["max_altitude_m"]:
        violations.append(f"Altitude exceeds limit: {data['altitude']} m > {rules['max_altitude_m']} m.")
        prevention_actions.append(f"Command: reduce altitude to {rules['max_altitude_m']} m or below.")

    elif data["altitude"] > 0.85 * rules["max_altitude_m"]:
        warnings.append("Altitude is approaching the regulatory limit.")

    if data["speed"] > rules["max_speed_kmh"]:
        violations.append(f"Speed exceeds limit: {data['speed']} km/h > {rules['max_speed_kmh']} km/h.")
        prevention_actions.append(f"Command: reduce speed to {rules['max_speed_kmh']} km/h or below.")

    elif data["speed"] > 0.85 * rules["max_speed_kmh"]:
        warnings.append("Speed is approaching the regulatory limit.")

    if data["near_airport"]:
        violations.append("Operation is near an airport.")
        prevention_actions.append("Command: stop mission or request aviation authority clearance.")

    if data["restricted_zone"]:
        violations.append("Drone is entering or operating in a restricted zone.")
        prevention_actions.append("Command: activate geofence and prevent entry.")

    if data["near_people"]:
        warnings.append("Operation is near people; additional safety controls may be required.")

    if violations:
        status = "❌ Not Compliant"
    elif warnings:
        status = "⚠️ Compliant With Caution"
    else:
        status = "✅ Compliant"

    return status, violations, warnings, prevention_actions

def assess_safety(data):
    safety_issues = []
    safety_warnings = []
    actions = []

    if data["battery"] < 20:
        safety_issues.append("Battery level is critically low.")
        actions.append("Command: Return to Home immediately.")
    elif data["battery"] < 35:
        safety_warnings.append("Battery level is low.")

    if data["gps"] < 50:
        safety_issues.append("GPS signal is weak.")
        actions.append("Command: hold position or return to home if stable navigation is not possible.")
    elif data["gps"] < 70:
        safety_warnings.append("GPS signal should be monitored.")

    if data["communication"] < 50:
        safety_issues.append("Communication link is unstable.")
        actions.append("Command: fail-safe return or controlled landing.")
    elif data["communication"] < 70:
        safety_warnings.append("Communication signal is reduced.")

    if data["motor_temp"] > 80:
        safety_issues.append("Motor temperature is too high.")
        actions.append("Command: reduce load or land for inspection.")
    elif data["motor_temp"] > 65:
        safety_warnings.append("Motor temperature is elevated.")

    if data["vibration"] > 75:
        safety_issues.append("Vibration level is abnormal.")
        actions.append("Command: land and inspect propellers/motors.")
    elif data["vibration"] > 55:
        safety_warnings.append("Vibration level is increasing.")

    if safety_issues:
        safety_status = "🔴 Unsafe"
    elif safety_warnings:
        safety_status = "🟡 Safe With Caution"
    else:
        safety_status = "🟢 Safe"

    return safety_status, safety_issues, safety_warnings, actions

def calculate_risk(data, violations, safety_issues):
    score = 0
    score += min(data["weight"], 50) * 0.4
    score += min(data["altitude"], 250) * 0.08
    score += min(data["speed"], 200) * 0.08

    if data["near_airport"]:
        score += 25
    if data["near_people"]:
        score += 15
    if data["restricted_zone"]:
        score += 30

    score += max(0, 35 - data["battery"]) * 0.8
    score += max(0, 70 - data["gps"]) * 0.5
    score += max(0, 70 - data["communication"]) * 0.5
    score += max(0, data["motor_temp"] - 60) * 0.6
    score += max(0, data["vibration"] - 50) * 0.5
    score += len(violations) * 10
    score += len(safety_issues) * 10

    score = round(min(score, 100), 1)

    if score <= 30:
        level = "Low Risk"
    elif score <= 65:
        level = "Medium Risk"
    else:
        level = "High Risk"

    return score, level

def final_decision(compliance_status, safety_status, violations, safety_issues):
    if violations or safety_issues:
        return "🛑 Mission Blocked / Corrective Action Required"
    if "Caution" in compliance_status or "Caution" in safety_status:
        return "⚠️ Mission Allowed With Monitoring"
    return "✅ Mission Approved"

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("Mission Setup")

authority = st.sidebar.selectbox("Regulatory Authority", list(REGULATIONS.keys()))
rules = REGULATIONS[authority]

scenario = st.sidebar.selectbox("Scenario Library", list(SCENARIOS.keys()))
preset = SCENARIOS[scenario]

st.sidebar.divider()
st.sidebar.write("Regulatory limits used in this prototype:")
st.sidebar.write(f"- Max altitude: {rules['max_altitude_m']} m")
st.sidebar.write(f"- Max speed: {rules['max_speed_kmh']} km/h")
st.sidebar.write(f"- Max weight: {rules['max_weight_kg']} kg")

# -----------------------------
# Input section
# -----------------------------
st.header("1. Live Drone Telemetry / Manual Input")

col1, col2, col3 = st.columns(3)

with col1:
    weight = st.number_input("Drone Weight (kg)", min_value=0.0, value=float(preset["weight"] if preset else 10), step=1.0)
    altitude = st.number_input("Altitude (m)", min_value=0.0, value=float(preset["altitude"] if preset else 50), step=5.0)
    speed = st.number_input("Speed (km/h)", min_value=0.0, value=float(preset["speed"] if preset else 30), step=5.0)

with col2:
    battery = st.slider("Battery Level (%)", 0, 100, int(preset["battery"] if preset else 80))
    gps = st.slider("GPS Signal Quality (%)", 0, 100, int(preset["gps"] if preset else 85))
    communication = st.slider("Communication Link (%)", 0, 100, int(preset["communication"] if preset else 90))

with col3:
    motor_temp = st.slider("Motor Temperature (°C)", 20, 120, int(preset["motor_temp"] if preset else 45))
    vibration = st.slider("Vibration Level (%)", 0, 100, int(preset["vibration"] if preset else 20))
    near_airport = st.checkbox("Near Airport?", value=bool(preset["near_airport"] if preset else False))
    near_people = st.checkbox("Near People?", value=bool(preset["near_people"] if preset else False))
    restricted_zone = st.checkbox("Restricted Zone?", value=bool(preset["restricted_zone"] if preset else False))

data = {
    "weight": weight,
    "altitude": altitude,
    "speed": speed,
    "battery": battery,
    "gps": gps,
    "communication": communication,
    "motor_temp": motor_temp,
    "vibration": vibration,
    "near_airport": near_airport,
    "near_people": near_people,
    "restricted_zone": restricted_zone,
}

if st.button("Analyze Mission", type="primary"):
    compliance_status, violations, warnings, prevention_actions = assess_compliance(data, rules)
    safety_status, safety_issues, safety_warnings, safety_actions = assess_safety(data)
    risk_score, risk_level = calculate_risk(data, violations, safety_issues)
    decision = final_decision(compliance_status, safety_status, violations, safety_issues)

    st.header("2. Mission Decision Dashboard")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Compliance", compliance_status)
    m2.metric("Safety", safety_status)
    m3.metric("Risk Score", f"{risk_score}/100")
    m4.metric("Risk Level", risk_level)

    if "Blocked" in decision:
        st.error(decision)
    elif "Monitoring" in decision:
        st.warning(decision)
    else:
        st.success(decision)

    st.header("3. Compliance Analysis")
    if violations:
        st.subheader("Violations")
        for item in violations:
            st.write(f"- {item}")
    else:
        st.write("No regulatory violations detected.")

    if warnings:
        st.subheader("Warnings")
        for item in warnings:
            st.write(f"- {item}")

    st.header("4. Automated Safety Check")
    if safety_issues:
        st.subheader("Safety Issues")
        for item in safety_issues:
            st.write(f"- {item}")
    else:
        st.write("No critical safety issues detected.")

    if safety_warnings:
        st.subheader("Safety Warnings")
        for item in safety_warnings:
            st.write(f"- {item}")

    st.header("5. Violation Prevention Actions")
    actions = prevention_actions + safety_actions
    if actions:
        for action in actions:
            st.write(f"- {action}")
    else:
        st.write("No prevention action required.")

    st.header("6. Educational Explain Mode")
    st.info(
        "AeroReg evaluates UAV operation by combining regulatory constraints "
        "such as altitude, speed, weight, and restricted-zone limitations with "
        "engineering safety checks such as battery, GPS, communication, motor temperature, "
        "and vibration. The system then classifies the mission and recommends preventive actions."
    )

    st.header("7. Compliance Log")
    st.code(
        f"""Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Authority: {authority}
Scenario: {scenario}
Decision: {decision}
Compliance Status: {compliance_status}
Safety Status: {safety_status}
Risk Score: {risk_score}
Risk Level: {risk_level}
""",
        language="text",
    )

st.divider()
st.caption("Prototype note: This tool is for educational simulation only and does not replace official aviation authority approval.")
