# Autonomous Cybersecurity System

### An Agentic AI Framework for Autonomous Cyber Threat Hunting and Intrusion Response

An AI-powered cybersecurity system designed to detect known and anomalous network threats, assess security risks, automate threat response, and improve detection strategies through reinforcement learning. The framework follows a closed-loop **Observe–Detect–Decide–Act–Learn (ODDAL)** approach to reduce response delays and minimize manual intervention in Security Operations Center (SOC) operations.

## Overview

Traditional intrusion detection systems primarily identify suspicious activity and rely on security analysts to investigate and respond. This project proposes an autonomous cybersecurity framework that integrates machine learning, anomaly detection, intelligent decision-making, automated mitigation, and continuous learning into a unified workflow.

The system combines supervised machine learning algorithms for known attack patterns with anomaly detection for potentially unfamiliar threats. A decision agent evaluates threat severity, detection confidence, and contextual risk before selecting an appropriate response.

## Key Features

- **Hybrid Threat Detection:** Combines Random Forest, XGBoost, and Logistic Regression with Isolation Forest-based anomaly detection.
- **Autonomous Threat Response:** Supports mitigation actions such as malicious IP blocking and compromised-host isolation.
- **Risk-Based Decision Making:** Evaluates detection probability, threat severity, and contextual risk.
- **Reinforcement Learning:** Uses Q-learning to refine decision policies based on feedback from previous responses.
- **SOC Dashboard:** Provides a web-based interface for visualizing security events and threat information.
- **Threat Analysis:** Supports traffic distribution analysis, threat trend monitoring, and comparative model evaluation.
- **Closed-Loop Automation:** Connects monitoring, detection, decision-making, response, and learning in a continuous workflow.

## System Workflow

The framework operates through five stages:

1. **Observe:** Collect and analyze network traffic, system logs, and user activity.
2. **Detect:** Apply supervised learning and anomaly detection to identify suspicious behavior.
3. **Decide:** Calculate a risk score using detection probability, threat severity, and contextual factors.
4. **Act:** Execute appropriate mitigation actions based on the assessed risk.
5. **Learn:** Use reinforcement learning feedback to improve detection thresholds and response policies.

## Technologies and Algorithms

| Component | Technology / Algorithm |
|---|---|
| Threat classification | Random Forest |
| Ensemble learning | XGBoost |
| Statistical classification | Logistic Regression |
| Anomaly detection | Isolation Forest |
| Reinforcement learning | Q-learning |
| Dataset for evaluation | UNSW-NB15 |
| Interface | Web-based SOC dashboard |
| Architecture | Multi-agent, closed-loop framework |

## Dataset

The research evaluates the proposed framework using the **UNSW-NB15 network intrusion detection dataset**, which contains normal network activities and multiple categories of malicious traffic.

The methodology includes:

- Data cleaning and preprocessing
- Feature normalization using Z-score normalization
- Training and testing dataset preparation
- Model evaluation using classification metrics

Large datasets are excluded from this repository where necessary because of GitHub file-size restrictions. Obtain the dataset from its authorized source before reproducing the experiments.

## Reported Experimental Results

The accompanying research presentation reports the following model performance:

| Metric | Random Forest | XGBoost | Baseline ML |
|---|---:|---:|---:|
| Accuracy | 98.6% | 99.1% | 92.4% |
| Precision | 97.9% | 98.7% | 91.2% |
| Recall | 98.2% | 99.0% | 90.8% |
| F1-score | 98.0% | 98.8% | 91.0% |

The presentation also reports response times of 120 ms for Random Forest and 105 ms for XGBoost, with automation rates of 92% and 95%, respectively. These are results reported in the accompanying project documents and should be independently reproduced before being treated as verified deployment performance.

## Project Structure

```text
autonomous-cybersecurity-system/
├── backend/                 # Backend and detection components
├── frontend/
│   └── dashboard/            # Web-based SOC dashboard
├── datasets/
│   └── TON_IoT/              # Available dataset files
├── .gitignore
└── README.md
```

The exact contents may vary depending on the current project version.

## Getting Started

### Prerequisites

- Python and the required backend dependencies
- Node.js and npm for the dashboard
- Git
- The required dataset files

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/Prasanna45773/autonomous-cybersecurity-system.git
cd autonomous-cybersecurity-system
```

**2. Set up the Python environment**

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install the backend dependencies using the project's dependency file, if provided:

```bash
pip install -r backend/requirements.txt
```

**3. Install dashboard dependencies**

```bash
cd frontend/dashboard
npm install
```

**4. Start the dashboard**

```bash
npm start
```

Follow the backend's actual configuration and startup instructions to run the complete system. The commands above are a general setup guide; verify the dependency-file path, entry point, environment variables, and service configuration against the current source code.

## Security and Responsible Use

- Test detection and response functions only in authorized environments.
- Use isolated test systems when evaluating automated blocking or host-isolation actions.
- Keep API keys, credentials, environment files, and sensitive logs out of version control.
- Review automated mitigation policies before enabling them on production networks.

## Limitations and Future Enhancements

- Validate detection performance against live network traffic.
- Improve detection of encrypted and high-dimensional traffic.
- Integrate external threat-intelligence feeds.
- Extend the framework to cloud-native and IoT environments.
- Explore privacy-preserving collaboration between Security Operations Centers.

## Research Publication

**Paper Title:** An Agentic AI Framework for Autonomous Cyber Threat Hunting and Intrusion Response

**Conference:** International Conference on Natural Language Processing and Computer Vision (ICNPCV)

**Paper ID:** ICNPCV2026-582

**Institution:** Department of Information Science and Engineering, BNM Institute of Technology, Bengaluru, India.

## Contributors

- Prasanna Kumar G
- Dhanya Spurthi A
- Kruthika B A
- Gururaj B K


## License

No license has been specified for this repository yet. Add an appropriate open-source license if you intend to permit others to reuse or modify the code.

---

**Disclaimer:** This project is intended for cybersecurity research, network intrusion detection, and authorized defensive security testing.
