# AeroReg Control Prototype

AeroReg Control is a Streamlit-based prototype for real-time UAV regulatory compliance, safety monitoring, and violation prevention.

## Features

- Regulatory authority selection: UAE GCAA, FAA, and EASA prototype rules
- Live telemetry/manual input dashboard
- Altitude, speed, and weight compliance checks
- Automated engineering safety checks:
  - battery
  - GPS signal
  - communication link
  - motor temperature
  - vibration
- Risk score and risk level classification
- Violation prevention actions
- Educational explain mode
- Compliance log

## Run Locally

Install requirements:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
python -m streamlit run app.py
```

## Deployment

Upload these files to a GitHub repository and deploy using Streamlit Community Cloud.

## Disclaimer

This project is an educational prototype and does not replace official aviation authority approval.