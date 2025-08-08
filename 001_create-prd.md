<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide.md -->
<!-- MODULE_REFERENCE: 400_migration-upgrade-guide.md -->
<!-- MODULE_REFERENCE: 400_testing-strategy-guide.md -->

<!-- MODULE_REFERENCE: 400_integration-patterns-guide.md -->
# Create PRD

<!-- ANCHOR: tldr -->
<a id="tldr"></a>

## 🔎 TL;DR

- Purpose: Turn a backlog item into a concise, testable PRD
- PRD Skip Rule: Skip when points < 5 AND score_total ≥ 3.0
- Output: Clear scope, acceptance criteria, quality gates
- Handoff: Feed this PRD into `002_generate-tasks.md`

<!-- ANCHOR: when-to-use -->
<a id="when-to-use"></a>

## When to use

- Use for high-risk or 5+ point items, or when score_total < 3.0
- Optional for smaller items where acceptance criteria are obvious

<!-- ANCHOR: prd-skip-rule -->
<a id="prd-skip-rule"></a>

### PRD Skip Rule (canonical)

- Skip PRD when: points < 5 AND score_total ≥ 3.0
- Otherwise, create a PRD with machine-verifiable acceptance criteria

<!-- ANCHOR: template -->
<a id="template"></a>

- **Impact**: Quantified benefits and outcomes

### **3. Solution Overview**

- **High-Level Solution**: Core approach and architecture
- **Key Features**: Main capabilities and functionality
- **Technical Approach**: Technology stack and implementation strategy
- **Integration Points**: How it connects with existing systems

### **4. Functional Requirements**

- **User Stories**: Detailed user scenarios and workflows
- **Feature Specifications**: Detailed feature requirements
- **Data Requirements**: Data models, storage, and processing needs
- **API Requirements**: External interfaces and integrations

### **5. Non-Functional Requirements**

- **Performance Requirements**: Response times, throughput, scalability
- **Security Requirements**: Authentication, authorization, data protection
- **Reliability Requirements**: Uptime, error rates, disaster recovery
- **Usability Requirements**: User experience, accessibility, internationalization

## **Enhanced Testing Requirements Section**

### **6. Testing Strategy**

- **Test Coverage Goals**: Percentage targets for different test types
- **Testing Phases**: Unit, integration, system, and acceptance testing
- **Automation Requirements**: What should be automated vs. manual
- **Test Environment Requirements**: Staging, testing, and production environments

### **7. Quality Assurance Requirements**

- **Code Quality Standards**: Coding standards, review processes
- **Performance Benchmarks**: Specific performance targets and thresholds
- **Security Validation**: Security testing requirements and compliance
- **User Acceptance Criteria**: How user acceptance will be validated

### **8. Implementation Quality Gates**

- **Development Phase Gates**:
  - [ ] **Requirements Review** - All requirements are clear and testable
  - [ ] **Design Review** - Architecture and design are approved
  - [ ] **Code Review** - All code has been reviewed and approved
  - [ ] **Testing Complete** - All tests pass with required coverage
  - [ ] **Performance Validated** - Performance meets requirements
  - [ ] **Security Reviewed** - Security implications considered and addressed
  - [ ] **Documentation Updated** - All relevant documentation is current
  - [ ] **User Acceptance** - Feature validated with end users

### **9. Testing Requirements by Component**

#### **Unit Testing Requirements**

- **Coverage Target**: Minimum 80% code coverage
- **Test Scope**: All public methods and critical private methods
- **Test Quality**: Tests must be isolated, deterministic, and fast
- **Mock Requirements**: External dependencies must be mocked
- **Edge Cases**: Boundary conditions and error scenarios must be tested

#### **Integration Testing Requirements**

- **Component Integration**: Test interactions between components
- **API Testing**: Validate all external interfaces and contracts
- **Data Flow Testing**: Verify data transformation and persistence
- **Error Propagation**: Test how errors propagate between components

#### **Performance Testing Requirements**

- **Response Time**: Define acceptable latency thresholds (e.g., < 200ms for API calls)
- **Throughput**: Specify requests per second requirements
- **Resource Usage**: Set memory and CPU limits
- **Scalability**: Test with increasing load levels
- **Concurrent Users**: Define maximum concurrent user capacity

#### **Security Testing Requirements**

- **Input Validation**: Test for injection attacks (SQL, XSS, prompt injection)
- **Authentication**: Validate user authentication and session management
- **Authorization**: Test access control and permission systems
- **Data Protection**: Verify encryption and secure data handling
- **Vulnerability Scanning**: Regular security scans and penetration testing

#### **Resilience Testing Requirements**

- **Error Handling**: Test graceful degradation under failure conditions
- **Recovery Mechanisms**: Validate automatic recovery from failures
- **Resource Exhaustion**: Test behavior under high load and resource constraints
- **Network Failures**: Test behavior during network interruptions
- **Data Corruption**: Test handling of corrupted or incomplete data

#### **Edge Case Testing Requirements**

- **Boundary Conditions**: Test with maximum/minimum values
- **Special Characters**: Validate Unicode and special character handling
- **Large Data Sets**: Test with realistic data volumes
- **Concurrent Access**: Test race conditions and thread safety
- **Malformed Input**: Test behavior with invalid or unexpected input

### **10. Monitoring and Observability**

- **Logging Requirements**: Structured logging with appropriate levels
- **Metrics Collection**: Performance and business metrics to track
- **Alerting**: Automated alerts for critical issues
- **Dashboard Requirements**: Real-time monitoring dashboards
- **Troubleshooting**: Tools and procedures for debugging issues

### **11. Deployment and Release Requirements**

- **Environment Setup**: Development, staging, and production environments
- **Deployment Process**: Automated deployment and rollback procedures
- **Configuration Management**: Environment-specific configuration
- **Database Migrations**: Schema changes and data migration procedures
- **Feature Flags**: Gradual rollout and feature toggling capabilities

## **PRD Output Format**

```markdown

# Product Requirements Document: [Project Name]

> ⚠️ **Auto-Skip Note**  
> This PRD was generated because either `points≥5` or `score_total<3.0`.  
> Remove this banner if you manually forced PRD creation.

## 1. Executive Summary

[Project overview, success metrics, timeline, stakeholders]

## 2. Problem Statement

[Current state, pain points, opportunity, impact]

## 3. Solution Overview

[High-level solution, key features, technical approach, integration points]

## 4. Functional Requirements

[User stories, feature specifications, data requirements, API requirements]

## 5. Non-Functional Requirements

[Performance, security, reliability, usability requirements]

## 6. Testing Strategy

[Test coverage goals, testing phases, automation requirements, test environments]

## 7. Quality Assurance Requirements

[Code quality standards, performance benchmarks, security validation, user acceptance criteria]

## 8. Implementation Quality Gates

[Development phase gates and completion criteria]

## 9. Testing Requirements by Component

[Detailed testing requirements for each component type]

## 10. Monitoring and Observability

[Logging, metrics, alerting, dashboard, troubleshooting requirements]

## 11. Deployment and Release Requirements

[Environment setup, deployment process, configuration management, database migrations, feature flags]

## 12. Risk Assessment and Mitigation

[Technical risks, timeline risks, resource risks, and mitigation strategies]

## 13. Success Criteria

[Measurable success criteria and acceptance criteria]
```

## **Special Instructions**

1. **Always include comprehensive testing requirements** for every component
2. **Specify performance benchmarks** with concrete numbers
3. **Include security considerations** for all user-facing features
4. **Add resilience testing** for critical system components
5. **Consider edge cases** and boundary conditions
6. **Define quality gates** for each major milestone
7. **Include monitoring and observability** requirements
8. **Specify error handling** and recovery procedures
9. **Align with backlog priorities** when planning task dependencies and effort
10. **Consider impact estimates** from backlog to ensure appropriate task scope
11. **Parse backlog table format** when provided with backlog ID
12. **Use points-based estimation** for task effort planning
13. **Track backlog status updates** as tasks are completed
14. **Consider backlog scoring** for prioritization when available
15. **Use scoring metadata** to inform effort and dependency planning

<!-- ANCHOR: acceptance-criteria -->
<a id="acceptance-criteria"></a>

This enhanced approach ensures that every PRD includes thorough testing requirements and quality gates, leading to more robust and reliable implementations.

<!-- ANCHOR: handoff-to-002 -->
<a id="handoff-to-002"></a>

## Handoff to task generation

- Next step: Use `002_generate-tasks.md` with this PRD (or a Backlog ID)
- Input → PRD file; Output → 2–4 hour tasks with dependencies and gates
