\n+## 🛡️ Constitution Security Hooks
\n+- Tie threat modeling and minimum scan requirements to constitution gates.
- Enforce scans on high‑risk changes; document exceptions with approvals.
- Surface security compliance status in deployments/ops metrics.
<!-- ANCHOR_KEY: security-best-practices -->
<!-- ANCHOR_PRIORITY: 20 -->

<!-- ROLE_PINS: ["coder", "implementer"] -->
# 🔒 Security Best Practices Guide

<!-- ANCHOR: tldr -->
{#tldr}

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
|  |  |  |

### CI Security Scans (from Comprehensive Guide)
- Bandit: `bandit -r src/`
- Safety: `safety check`
- Enforce scans on high‑risk changes; document exceptions and approvals

- **what this file is**: Security architecture, controls, and incident response for the system.

- **read when**: Making risky changes, setting policies, or responding to security events.

- **do next**: Review "Security Architecture", "Access Control", and "Incident Response".

- **anchors**: `security architecture`, `access control`, `data protection`, `network security`, `ai model security`,
`incident response`, `security checklist`

## 🎯 **Current Status**-**Status**: ✅ **ACTIVE**- Security practices maintained

- **Priority**: 🔥 Critical - System security and threat mitigation

- **Points**: 5 - High complexity, security critical

- **Dependencies**: 400_guides/400_context-priority-guide.md, 400_guides/400_deployment-environment-guide.md

- **Next Steps**: Update security practices as threats evolve

### **3. AI-Specific Threats**-**Prompt Injection**: Manipulating AI models to bypass security controls

- **Model Poisoning**: Corrupting training data or model weights

- **Output Manipulation**: Forcing AI models to generate harmful content

- **Privacy Violations**: AI models revealing sensitive information from training data

### **Risk Assessment Matrix**| Threat | Likelihood | Impact | Risk Level | Mitigation |

|--------|------------|--------|------------|------------|
| Prompt Injection | High | High | 🔴 Critical | Input validation, prompt sanitization |
| Data Exfiltration | Medium | High | 🟡 High | Access controls, encryption |
| Denial of Service | Medium | Medium | 🟡 High | Rate limiting, monitoring |
| Configuration Errors | High | Medium | 🟡 High | Automated validation, testing |
| Accidental Data Exposure | High | High | 🔴 Critical | Pre-commit hooks, scanning |

- --

## 🏗️ Security Architecture

### **Defense in Depth Strategy**

```text
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                         │
├─────────────────────────────────────────────────────────────┤
│ 1. Physical Security (Local Development)                  │
│ 2. Network Security (Firewall, VPN)                       │
│ 3. Application Security (Input Validation, Auth)          │
│ 4. Data Security (Encryption, Access Controls)            │
│ 5. AI Model Security (Prompt Sanitization, Output Filter) │
│ 6. Monitoring & Response (Logs, Alerts, IR)              │
└─────────────────────────────────────────────────────────────┘
```

### **Security Components**

#### **1. Input Validation System**
- **Location**: `dspy-rag-system/src/utils/prompt_sanitizer.py`
- **Purpose**: Sanitize all AI prompts and user inputs
- **Features**: Regex patterns, whitelist logic, security validation

#### **2. Access Control System**
- **Location**: `dspy-rag-system/src/utils/security.py`
- **Purpose**: Manage user permissions and authentication
- **Features**: Role-based access, session management

#### **3. Secrets Management**
- **Location**: `dspy-rag-system/src/utils/secrets_manager.py`
- **Purpose**: Secure credential storage and retrieval
- **Features**: Environment validation, keyring integration

#### **4. Monitoring & Alerting**
- **Location**: `dspy-rag-system/src/monitoring/`

## 🛡️ ADVANCED SECURITY & COMPLIANCE INTEGRATION

### **Intelligent Security Orchestration**

**Purpose**: Create sophisticated security patterns that adapt to threats, learn from incidents, and provide proactive protection.

**Key Principles**:
- **Threat-aware security**: Adapt security measures based on current threat landscape
- **Learning from incidents**: Improve security based on incident patterns and outcomes
- **Proactive protection**: Anticipate threats and implement preventive measures
- **Compliance automation**: Automate compliance checks and reporting

### **Implementation Patterns**

#### **1. Adaptive Security Framework**
```python
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio
import time

@dataclass
class SecurityContext:
    """Context for adaptive security decisions."""
    current_threat_level: str
    system_state: Dict[str, Any]
    recent_incidents: List[Dict[str, Any]]
    compliance_requirements: List[str]
    resource_constraints: Dict[str, float]

class AdaptiveSecurityFramework:
    """Intelligent security orchestration framework."""

    def __init__(self):
        self.security_policies = {}
        self.threat_models = {}
        self.incident_history = []
        self.learning_engine = None

    async def apply_security_measures(self, context: SecurityContext) -> Dict[str, Any]:
        """Apply adaptive security measures based on context."""

        # Analyze current threat landscape
        threat_analysis = self._analyze_threat_landscape(context)

        # Adapt security policies
        adapted_policies = self._adapt_security_policies(context, threat_analysis)

        # Apply security measures
        security_result = await self._apply_measures(adapted_policies, context)

        # Update learning models
        self._update_security_models(context, security_result)

        return security_result

    def _analyze_threat_landscape(self, context: SecurityContext) -> Dict[str, Any]:
        """Analyze current threat landscape."""
        return {
            "threat_level": context.current_threat_level,
            "vulnerability_scan": self._scan_vulnerabilities(context.system_state),
            "incident_patterns": self._analyze_incident_patterns(context.recent_incidents),
            "compliance_gaps": self._identify_compliance_gaps(context.compliance_requirements)
        }

    def _adapt_security_policies(self, context: SecurityContext,
                                threat_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt security policies based on threat analysis."""
        adapted_policies = {}

        # Threat level-based adaptation
        if threat_analysis["threat_level"] == "HIGH":
            adapted_policies["input_validation"] = "STRICT"
            adapted_policies["rate_limiting"] = "AGGRESSIVE"
            adapted_policies["monitoring"] = "INTENSIVE"
        elif threat_analysis["threat_level"] == "MEDIUM":
            adapted_policies["input_validation"] = "MODERATE"
            adapted_policies["rate_limiting"] = "STANDARD"
            adapted_policies["monitoring"] = "STANDARD"
        else:
            adapted_policies["input_validation"] = "BASIC"
            adapted_policies["rate_limiting"] = "LENIENT"
            adapted_policies["monitoring"] = "BASIC"

        # Vulnerability-based adaptation
        if threat_analysis["vulnerability_scan"]["critical_count"] > 0:
            adapted_policies["emergency_mode"] = True
            adapted_policies["additional_scanning"] = True

        return adapted_policies
```

#### **2. Intelligent Threat Detection**
```python
class IntelligentThreatDetection:
    """Intelligent threat detection and response system."""

    def __init__(self):
        self.detection_models = {}
        self.response_actions = {}
        self.threat_intelligence = {}

    async def detect_threats(self, system_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect threats using intelligent analysis."""
        detected_threats = []

        # Behavioral analysis
        behavioral_threats = self._analyze_behavioral_patterns(system_data)
        detected_threats.extend(behavioral_threats)

        # Anomaly detection
        anomaly_threats = self._detect_anomalies(system_data)
        detected_threats.extend(anomaly_threats)

        # Pattern matching
        pattern_threats = self._match_known_patterns(system_data)
        detected_threats.extend(pattern_threats)

        # AI-specific threats
        ai_threats = self._detect_ai_specific_threats(system_data)
        detected_threats.extend(ai_threats)

        return detected_threats

    def _analyze_behavioral_patterns(self, system_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze behavioral patterns for threat detection."""
        threats = []

        # Analyze user behavior patterns
        user_patterns = self._extract_user_patterns(system_data)
        suspicious_patterns = self._identify_suspicious_patterns(user_patterns)

        for pattern in suspicious_patterns:
            threats.append({
                "type": "behavioral",
                "severity": pattern["risk_score"],
                "description": f"Suspicious behavior pattern: {pattern['description']}",
                "confidence": pattern["confidence"],
                "recommended_action": pattern["recommended_action"]
            })

        return threats

    def _detect_ai_specific_threats(self, system_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect AI-specific security threats."""
        threats = []

        # Prompt injection detection
        if "prompt_injection_attempts" in system_data:
            for attempt in system_data["prompt_injection_attempts"]:
                threats.append({
                    "type": "prompt_injection",
                    "severity": "HIGH",
                    "description": f"Prompt injection attempt detected: {attempt['pattern']}",
                    "confidence": attempt["confidence"],
                    "recommended_action": "BLOCK_AND_LOG"
                })

        # Model poisoning detection
        if "suspicious_training_data" in system_data:
            threats.append({
                "type": "model_poisoning",
                "severity": "CRITICAL",
                "description": "Suspicious training data patterns detected",
                "confidence": 0.85,
                "recommended_action": "ISOLATE_AND_INVESTIGATE"
            })

        return threats
```

#### **3. Compliance Automation System**
```python
class ComplianceAutomationSystem:
    """Automated compliance checking and reporting system."""

    def __init__(self):
        self.compliance_frameworks = {}
        self.check_engines = {}
        self.reporting_templates = {}

    async def run_compliance_check(self, framework: str,
                                 system_state: Dict[str, Any]) -> Dict[str, Any]:
        """Run automated compliance check for specified framework."""

        if framework not in self.compliance_frameworks:
            raise ValueError(f"Unknown compliance framework: {framework}")

        framework_config = self.compliance_frameworks[framework]
        check_results = {}

        # Run all required checks
        for check_name, check_config in framework_config["checks"].items():
            check_engine = self.check_engines.get(check_config["engine"])
            if check_engine:
                result = await check_engine.run_check(check_config, system_state)
                check_results[check_name] = result

        # Generate compliance report
        compliance_report = self._generate_compliance_report(
            framework, check_results, system_state
        )

        return compliance_report

    def _generate_compliance_report(self, framework: str,
                                  check_results: Dict[str, Any],
                                  system_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""

        # Calculate compliance scores
        overall_score = self._calculate_compliance_score(check_results)

        # Identify compliance gaps
        compliance_gaps = self._identify_compliance_gaps(check_results)

        # Generate recommendations
        recommendations = self._generate_recommendations(compliance_gaps)

        report = {
            "framework": framework,
            "timestamp": time.time(),
            "overall_score": overall_score,
            "compliance_status": "COMPLIANT" if overall_score >= 0.9 else "NON_COMPLIANT",
            "check_results": check_results,
            "compliance_gaps": compliance_gaps,
            "recommendations": recommendations,
            "next_review_date": self._calculate_next_review_date(framework)
        }

        return report
```

### **Integration with Development Workflow**

#### **Security Gates in CI/CD**
```python
class SecurityGates:
    """Security gates for CI/CD pipeline integration."""

    def __init__(self):
        self.security_scanners = {}
        self.thresholds = {}
        self.remediation_actions = {}

    async def run_security_gates(self, change_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run security gates for a change."""

        gate_results = {}

        # Run all configured security gates
        for gate_name, gate_config in self.security_scanners.items():
            scanner = gate_config["scanner"]
            threshold = self.thresholds.get(gate_name, 0.0)

            result = await scanner.scan(change_data)
            gate_results[gate_name] = {
                "passed": result["score"] >= threshold,
                "score": result["score"],
                "threshold": threshold,
                "findings": result["findings"]
            }

        # Determine overall gate status
        all_passed = all(result["passed"] for result in gate_results.values())

        return {
            "overall_status": "PASSED" if all_passed else "FAILED",
            "gate_results": gate_results,
            "remediation_required": not all_passed
        }
```

#### **AI Security Integration**
```python
class AISecurityIntegration:
    """AI-specific security integration patterns."""

    def __init__(self):
        self.prompt_validators = {}
        self.output_filters = {}
        self.model_monitors = {}

    async def validate_ai_interaction(self, prompt: str,
                                    model_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate AI interaction for security compliance."""

        validation_result = {
            "prompt_validation": await self._validate_prompt(prompt, model_config),
            "model_security": await self._check_model_security(model_config),
            "output_safety": await self._validate_output_safety(model_config)
        }

        # Determine overall security status
        all_valid = all(result["valid"] for result in validation_result.values())

        return {
            "secure": all_valid,
            "validation_details": validation_result,
            "recommendations": self._generate_security_recommendations(validation_result)
        }
```

- **Purpose**: Real-time security monitoring and incident detection

- **Features**: Health checks, metrics collection, alert callbacks

- --

## 🔐 Access Control

### **Authentication Methods**

For comprehensive authentication patterns and security implementations, see
[400_comprehensive-coding-best-practices.md](400_comprehensive-coding-best-practices.md)
security section.

#### **1. Local Development Authentication**
- Environment-based authentication patterns
- See comprehensive guide for implementation examples

#### **2. API Authentication**
- API key validation patterns
- See comprehensive guide for security best practices

#### **3. Database Access Control**```sql
- - Role-based database access
CREATE ROLE ai_developer WITH LOGIN PASSWORD 'secure_password';
GRANT SELECT, INSERT, UPDATE ON episodic_logs TO ai_developer;
GRANT USAGE ON SCHEMA public TO ai_developer;

```bash

### **Permission Levels**| Role | Permissions | Access Level |
|------|-------------|--------------|
|**Admin**| Full system access | All components |
|**Developer**| Code and data access | Development environment |
|**AI Agent**| Limited API access | Specific endpoints |
|**Monitor**| Read-only access | Logs and metrics |

- --

## 🛡️ Data Protection

### **Encryption Standards**####**1. Data at Rest**-**Database**: PostgreSQL with encrypted connections

- **Files**: Sensitive files encrypted with AES-256

- **Secrets**: Keyring integration for secure storage

#### **2. Data in Transit**-**HTTPS**: All web communications encrypted

- **API**: TLS 1.3 for all API communications

- **Database**: SSL/TLS for database connections

#### **3. AI Model Data**-**Input Sanitization**: All prompts validated and sanitized

- **Output Filtering**: AI responses filtered for sensitive data

- **Cache Security**: Vector cache encrypted and access-controlled

### **Data Classification**| Classification | Examples | Protection Level |
|----------------|----------|------------------|
|**Public**| Documentation, guides | Basic access control |
|**Internal**| Development notes, configs | Role-based access |
|**Confidential**| API keys, passwords | Encryption required |
|**Restricted**| User data, model outputs | Strict access controls |

- --

## 🌐 Network Security

### **Local Development Security**####**1. Firewall Configuration**
- Network security configuration patterns
- See [400_comprehensive-coding-best-practices.md](400_comprehensive-coding-best-practices.md) for comprehensive firewall and network security implementation examples

#### **2. VPN Requirements**-**Development**: VPN required for external API access

- **Production**: All external communications through VPN

- **Monitoring**: VPN logs monitored for suspicious activity

#### **3. Network Segmentation**```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Development   │    │   AI Models     │    │   Database      │
│   Environment   │◄──►│   (Local/API)   │◄──►│   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘

```text

- --

## 🤖 AI Model Security

### **Prompt Security**####**1. Input Validation**
- Prompt validation and sanitization patterns
- See [400_comprehensive-coding-best-practices.md](400_comprehensive-coding-best-practices.md) for comprehensive input validation implementation examples

#### **2. Output Filtering**
- AI response filtering patterns
- See comprehensive guide for security filtering implementation examples

#### **3. Model Access Control**
- AI model access control patterns
- See comprehensive guide for access control implementation examples

### **AI Model Threats & Mitigations**| Threat | Description | Mitigation |
|--------|-------------|------------|
|**Prompt Injection**| Malicious prompts to bypass controls | Input sanitization, output filtering |
|**Data Leakage**| AI revealing sensitive training data | Output filtering, access controls |
|**Model Poisoning**| Corrupting model with malicious data | Training data validation |
|**Resource Abuse**| Excessive API calls or token usage | Rate limiting, usage monitoring |

- --

## 🚨 Incident Response

### **Incident Classification**####**1. Critical Incidents (Response: < 1 hour)**- Data breach or unauthorized access

- System compromise or malware detection

- AI model security violations

- Network intrusion attempts

#### **2. High Priority (Response: < 4 hours)**- Failed authentication attempts

- Unusual system behavior

- Performance degradation

- Configuration errors

#### **3. Medium Priority (Response: < 24 hours)**- Minor security alerts

- Performance issues

- Documentation updates needed

### **Response Procedures**####**1. Detection & Alerting**```python

# Security monitoring setup

def security_alert(incident_type: str, details: dict):

    # Send immediate alert

    send_alert(f"SECURITY ALERT: {incident_type}", details)

    # Log incident

    log_security_incident(incident_type, details)

    # Trigger response procedures

    trigger_incident_response(incident_type)

```text

## **2. Containment Procedures**```bash

# Emergency containment script

# !/bin/bash

# emergency_containment.sh

echo "🚨 EMERGENCY CONTAINMENT PROCEDURE"
echo "1. Isolating affected systems..."
echo "2. Blocking suspicious IP addresses..."
echo "3. Disabling compromised accounts..."
echo "4. Initiating backup procedures..."

```text

## **3. Recovery Procedures**```python

# Recovery automation

def initiate_recovery(incident_type: str):
    if incident_type == "data_breach":
        rotate_all_secrets()
        restore_from_backup()
        update_access_controls()
    elif incident_type == "system_compromise":
        isolate_affected_systems()
        restore_clean_environment()
        validate_system_integrity()

```text

## **Incident Response Team**| Role | Responsibilities | Contact |
|------|------------------|---------|
|**Incident Commander**| Overall response coordination | Primary developer |
|**Technical Lead**| Technical investigation and remediation | AI system expert |
|**Communications**| Stakeholder updates and documentation | Documentation lead |
|**Legal/Compliance**| Regulatory requirements and reporting | External consultant |

- --

## 📊 Security Monitoring

### **Monitoring Components**####**1. Real-time Monitoring**```python

# Security monitoring setup

SECURITY_MONITORING_CONFIG = {
    "log_level": "INFO",
    "alert_thresholds": {
        "failed_logins": 5,
        "api_errors": 10,
        "memory_usage": 90,
        "disk_usage": 85
    },
    "monitoring_interval": 60  # seconds

}

```bash

## **2. Security Metrics**-**Authentication Failures**: Track failed login attempts

- **API Usage Patterns**: Monitor for unusual API calls

- **System Performance**: Monitor for performance anomalies

- **Data Access Patterns**: Track database access patterns

### **3. Alert Channels**```python

# Alert configuration

ALERT_CHANNELS = {
    "critical": ["email", "sms", "dashboard"],
    "high": ["email", "dashboard"],
    "medium": ["dashboard"],
    "low": ["logs"]
}

```text

## **Security Dashboard**####**1. Real-time Security Status**```text
🔒 Security Dashboard
├── 🟢 System Status: Secure
├── 🟡 Active Alerts: 2
├── 📊 Threat Level: Low
└── 🛡️ Last Scan: 2 minutes ago

```

### **2. Security Metrics**-**Vulnerability Scan Results**-**Access Control Status**-**Encryption Status**-**Backup Status**---

## 📋 Compliance & Standards

### **Security Standards**####**1. OWASP Top 10 Compliance**-**A01:2021 - Broken Access Control**: Implemented role-based access

- **A02:2021 - Cryptographic Failures**: TLS 1.3, AES-256 encryption

- **A03:2021 - Injection**: Input validation and sanitization

- **A04:2021 - Insecure Design**: Security-first architecture

- **A05:2021 - Security Misconfiguration**: Automated configuration validation

#### **2. AI Security Best Practices**-**Input Validation**: All AI inputs sanitized

- **Output Filtering**: AI outputs filtered for sensitive data

- **Access Controls**: Model access restricted by role

- **Monitoring**: AI interactions logged and monitored

#### **3. Data Protection Standards**-**Encryption**: Data encrypted at rest and in transit

- **Access Controls**: Principle of least privilege

- **Audit Logging**: All access attempts logged

- **Data Classification**: Sensitive data properly classified

### **Compliance Checklist**- [ ]**Access Controls**: Role-based access implemented

- [ ] **Encryption**: Data encrypted at rest and in transit

- [ ] **Input Validation**: All inputs validated and sanitized

- [ ] **Monitoring**: Security monitoring active

- [ ] **Incident Response**: Procedures documented and tested

- [ ] **Backup Security**: Backups encrypted and access-controlled

- [ ] **Network Security**: Firewall and VPN configured

- [ ] **AI Security**: Model inputs/outputs secured

- [ ] **Documentation**: Security procedures documented

- [ ] **Training**: Security awareness training completed

- --

## ✅ Security Checklist

### **Daily Security Tasks**- [ ] Review security alerts and logs

- [ ] Check system performance and resource usage

- [ ] Verify backup integrity

- [ ] Update security patches if available

- [ ] Review access control logs

### **Weekly Security Tasks**- [ ] Run vulnerability scans

- [ ] Review and update security configurations

- [ ] Test incident response procedures

- [ ] Update security documentation

- [ ] Review AI model security settings

### **Monthly Security Tasks**- [ ] Conduct security audit

- [ ] Review and update threat model

- [ ] Test disaster recovery procedures

- [ ] Update security training materials

- [ ] Review compliance status

### **Quarterly Security Tasks**- [ ] Conduct penetration testing

- [ ] Review and update security policies

- [ ] Update incident response procedures

- [ ] Conduct security awareness training

- [ ] Review and update risk assessments

- --

## 🚨 Emergency Procedures

### **Immediate Response (0-15 minutes)**

1.**Assess the situation**- Determine incident type and severity
2.**Contain the threat**- Isolate affected systems
3.**Alert stakeholders**- Notify incident response team
4.**Document everything**- Begin incident documentation

### **Short-term Response (15 minutes - 4 hours)**

1.**Investigate root cause**- Determine how the incident occurred
2.**Implement fixes**- Apply security patches or configuration changes
3.**Monitor systems**- Watch for additional threats
4.**Communicate status**- Update stakeholders on progress

### **Long-term Response (4 hours - 1 week)**

1.**Complete investigation**- Full technical and forensic analysis
2.**Implement permanent fixes**- Address root causes
3.**Update procedures**- Improve security based on lessons learned
4.**Document lessons learned**- Update security documentation

### **Recovery Procedures**

1.**System restoration**- Restore systems from clean backups
2.**Security validation**- Verify systems are secure
3.**Monitoring enhancement**- Improve monitoring based on incident
4.**Training updates**- Update security training materials

- --

## 📞 Emergency Contacts

### **Primary Contacts**-**Security Lead**: Primary developer (24/7)

- **Technical Lead**: AI system expert

- **Management**: Project stakeholder

### **External Contacts**-**Cybersecurity Consultant**: External security expert

- **Legal Counsel**: For compliance and legal issues

- **Insurance Provider**: For incident reporting

### **Emergency Numbers**-**Security Hotline**: Internal number

- **IT Support**: Internal number

- **External Security**: External number

- --

## 📚 Additional Resources

### **Security Documentation**-**OWASP Top 10**: <https://owasp.org/Top10/>

- **AI Security Guidelines**: <https://ai.gov/security/>

- **NIST Cybersecurity Framework**: <https://www.nist.gov/cyberframework>

### **Tools and Scripts**-**Security Scanner**: `scripts/security_scan.py`

- **Vulnerability Checker**: `scripts/vulnerability_check.py`

- **Incident Response**: `scripts/incident_response.py`

### **Training Resources**-**Security Awareness Training**: Quarterly sessions

- **Incident Response Drills**: Monthly exercises

- **AI Security Training**: Specialized training for AI systems

- --

- Last Updated: 2025-08-30*
- Next Review: Monthly*
- Security Level: Confidential*
