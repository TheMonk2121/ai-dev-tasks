# PRD: Global Bug-Fix Playbook + Enforcement Layers (Cursor + CI)

**Backlog Item**: B-182
**Status**: Ready for Implementation
**Estimated Hours**: 4 hours

**Dependencies**:
- **Upstream**: None (can be implemented independently)
- **Downstream**: B-183 (Feature Refactor Framework depends on this)
- **Blocking**: None

**Impact Scope**:
- **Direct**: Debugging workflow, Cursor integration, CI validation, hot-zone rules
- **Indirect**: All future bugfixes, development velocity, regression prevention
- **Public Contracts**: None (internal tooling only)

## TL;DR

**What**: Introduce a global Bug-Fix Playbook and three-layer enforcement system to bring CS-level rigor to solo debugging without slowing velocity.

**Why**: AI (and tired humans) often fix bugs locally and miss downstream contracts → regressions, drift, rework. We need debug-velocity rigor integrated with our pipeline and Cursor.

**How**: Three-layer system - Preset (soft), Hot-Zone Rules (targeted), PR/CI Guard (hard) - with comprehensive documentation and automation.

**Impact**: Reduce regression rate in hot zones by ≥30%, maintain velocity, enforce test coverage on bugfixes.

---

## 1. Problem Statement

### Current State
- AI (and tired humans) often fix bugs locally and miss downstream contracts
- Bug fixes bypass existing 000→003 governance rigor to move fast
- Regressions, drift, and rework occur due to incomplete debugging
- No structured approach to bug fixing that balances velocity with rigor

### Pain Points
- Inconsistent debugging practices across the codebase
- Missing test coverage on bugfixes leading to regressions
- No guardrails for fragile modules (validator, vector_store, dashboard, archive)
- Lack of structured problem documentation and resolution tracking

### Root Cause
- Debugging is often done in isolation without systematic approach
- No integration between debugging workflow and existing governance
- Missing enforcement layers to ensure quality without slowing velocity

---

## 2. Solution Overview

### High-Level Solution
A three-layer enforcement system that brings CS-level rigor to solo debugging:

1. **Layer A – Preset (soft)**: One-keystroke Chat Preset ("Run Bug-Fix Playbook") that injects structured prompt
2. **Layer B – Hot-Zone Rules (targeted)**: Multi-framework aware Cursor rules scoped to fragile modules with commit message detection
3. **Layer C – PR/CI Guard (hard)**: PR template sections + CI enforcement based on Conventional Commits

### Key Features
- **Global Bug-Fix Playbook**: Structured, versioned debugging workflow
- **Cursor Integration**: Chat preset with keyboard shortcut (⌘⌥B / Ctrl+Alt+B)
- **Hot-Zone Protection**: Multi-framework aware rules for fragile modules with commit detection
- **PR Template Enhancement**: Mandatory bug snapshot and test coverage sections
- **CI Enforcement**: Automated validation of bugfix PR requirements
- **Quick Reference**: Easy-to-find documentation with hotkey reminders

### Technical Approach
- **Documentation-First**: Markdown-based playbook with clear structure
- **Cursor Native**: Leverage existing Cursor capabilities (presets, rules)
- **CI/CD Integration**: GitHub Actions for automated validation
- **Progressive Enforcement**: Soft → targeted → hard layers

### Integration Points
- **Existing Governance**: Complements 000→003 workflow without replacing it
- **Cursor IDE**: Native integration via presets and folder-specific rules
- **GitHub Workflow**: PR templates and CI checks
- **Testing Framework**: Enforces test coverage requirements

---

## 3. Functional Requirements

### User Stories

#### US-001: Developer Uses Bug-Fix Playbook Preset
**As a** developer debugging an issue
**I want to** use a keyboard shortcut to apply the structured bug-fix playbook
**So that** I can follow a consistent debugging process without remembering the steps

**Acceptance Criteria:**
- Preset "Run Bug-Fix Playbook" exists in Cursor
- Keyboard shortcut ⌘⌥B (macOS) / Ctrl+Alt+B (Windows/Linux) works
- Preset injects structured prompt with all required sections
- Quick reference document shows how to configure shortcut

#### US-002: Hot-Zone Rules Protect Fragile Modules
**As a** developer editing files in fragile modules
**I want to** be guided to the appropriate framework based on my commit message
**So that** I use the right level of rigor for my changes

**Acceptance Criteria:**
- Cursor rules exist for `src/validator/**`, `src/vector_store/**`, `src/dashboard/**`, `scripts/archive_*.py`
- Rules detect commit message prefixes (fix:, refactor:, feat:)
- Rules suggest appropriate framework (004, 005, 001-003) based on commit type
- Rules provide clear guidance without being intrusive

#### US-003: PR Template Enforces Bug Documentation
**As a** developer creating a bugfix PR
**I want to** be guided to include required bug documentation
**So that** the fix is properly documented and testable

**Acceptance Criteria:**
- PR template includes "Bug Snapshot" section
- Template requires "Didn't Touch" and "Blast Radius" documentation
- Template enforces test plan documentation
- Template is automatically applied to bugfix PRs

#### US-004: CI Validates Framework Requirements
**As a** developer submitting a PR
**I want** automated validation based on my commit message
**So that** the appropriate framework is enforced consistently

**Acceptance Criteria:**
- CI validates commit message prefixes (fix:, refactor:, feat:)
- CI enforces appropriate framework sections based on commit type
- CI provides clear error messages for framework violations
- CI maintains performance (<30 seconds)

#### US-005: Commit Message Detection Guides Framework Selection
**As a** developer writing commit messages
**I want to** be guided to the appropriate framework based on my commit prefix
**So that** I use the right level of rigor for my changes

**Acceptance Criteria:**
- Cursor detects commit message prefixes (fix:, refactor:, feat:)
- Cursor suggests appropriate framework (004, 005, 001-003)
- Cursor provides quick reference to framework selection
- Cursor integrates with existing presets and rules

### Feature Specifications

#### Bug-Fix Playbook Structure
```
## Problem Snapshot
- Title:
- Context (where/when):
- Observed vs Expected:
- Logs / Error:
- Environment:
- Dependencies: Direct | Upstream | Downstream
- Invariants (2–5 truths that must hold):

## Dual Review
### 🔴 Red (risks / root causes / questions)
### 🔵 Blue (minimal viable diff + test strategy)

## Resolution Check
- Chosen Fix:
- Didn't Touch (and why):
- Blast Radius: Direct | Upstream | Downstream | Public contracts
- Confidence (0–1):
- Test Plan: Repro → Guardrail
- Rollout & Observe (optional): flag, log, metric
```

#### Cursor Preset Content
- Role definition: "You are a senior debugging assistant"
- Structured prompt with all required sections
- Clear instructions for minimal diff and guardrail test
- Self-review requirements for regressions/security

#### Hot-Zone Rules Content
- Trigger: File edits in protected directories + commit message detection
- Requirement: Suggest appropriate framework based on commit prefix
- Focus: Multi-framework guidance (004, 005, 001-003)
- Format: Concise, actionable guidance with framework selection

#### PR Template Sections
- **Type**: Feature/Bugfix/Chore selection
- **Bug Snapshot**: Context, observed vs expected, logs, dependencies, invariants
- **Fix Plan**: Minimal diff, didn't touch, test plan, blast radius
- **Validation**: Confidence level, optional rollout/observe details

#### CI Guard Logic
- **Trigger**: Commit message prefixes (fix:, refactor:, feat:)
- **Validation**: Appropriate framework sections based on commit type
- **Enforcement**: Framework compliance based on Conventional Commits
- **Output**: Clear pass/fail with actionable error messages

### Data Requirements
- **Playbook Versioning**: Track playbook versions and updates
- **Usage Metrics**: Track preset usage and rule triggers
- **Compliance Tracking**: Monitor PR template completion rates
- **Test Coverage**: Enforce minimum test coverage on bugfixes

### API Requirements
- **Cursor API**: Integration with Cursor preset and rule systems
- **GitHub API**: PR template and CI check integration
- **File System**: Read/write access for documentation and configuration

---

## 4. Non-Functional Requirements

### Performance Requirements
- **Preset Response Time**: < 1 second for preset injection
- **CI Check Duration**: < 30 seconds for validation
- **Rule Trigger Latency**: < 500ms for Cursor rule display
- **Documentation Load Time**: < 2 seconds for quick reference

### Security Requirements
- **Input Validation**: Sanitize all user inputs in PR templates
- **Access Control**: Ensure only authorized users can modify playbook
- **Audit Trail**: Log all playbook usage and rule triggers
- **Secure Storage**: Protect sensitive information in bug snapshots

### Reliability Requirements
- **CI Check Uptime**: 99.9% availability for bugfix validation
- **Preset Reliability**: 99.5% success rate for preset injection
- **Rule Consistency**: Consistent behavior across different Cursor versions
- **Error Handling**: Graceful degradation when components fail

### Usability Requirements
- **Keyboard Shortcut**: Intuitive and memorable (⌘⌥B / Ctrl+Alt+B)
- **Documentation Clarity**: Self-explanatory quick reference
- **Error Messages**: Clear, actionable feedback for failures
- **Progressive Disclosure**: Show complexity only when needed

---

## 5. Testing Strategy

### Test Coverage Goals
- **Unit Tests**: 90% coverage for CI guard logic
- **Integration Tests**: 85% coverage for Cursor integration
- **End-to-End Tests**: 80% coverage for complete workflow
- **Documentation Tests**: 100% coverage for link validation

### Testing Phases
1. **Unit Testing**: Individual component validation
2. **Integration Testing**: Cursor preset and rule integration
3. **System Testing**: End-to-end workflow validation
4. **Acceptance Testing**: User acceptance validation

### Automation Requirements
- **Automated**: CI guard logic, preset validation, rule testing
- **Manual**: User experience testing, keyboard shortcut validation
- **Semi-Automated**: Documentation link checking, template validation

### Test Environment Requirements
- **Development**: Local Cursor environment for preset testing
- **Staging**: GitHub test repository for CI validation
- **Production**: Live repository with gradual rollout

---

## 6. Quality Assurance Requirements

### Code Quality Standards
- Follow comprehensive coding best practices from `400_guides/400_comprehensive-coding-best-practices.md`
- Maintain consistent documentation standards
- Ensure proper error handling and logging
- Follow security best practices for all integrations

### Performance Benchmarks
- **Preset Injection**: < 1 second response time
- **CI Validation**: < 30 seconds total duration
- **Rule Processing**: < 500ms trigger latency
- **Documentation Access**: < 2 seconds load time

### Security Validation
- Input sanitization for all user-provided content
- Secure handling of sensitive information in bug snapshots
- Proper access controls for playbook modifications
- Audit logging for all system interactions

### User Acceptance Criteria
- **Usability**: 95% of developers can use preset without training
- **Adoption**: 80% of bugfix PRs include required documentation
- **Compliance**: 90% of hot-zone edits follow playbook structure
- **Satisfaction**: 4.5/5 rating on developer experience survey

---

## 7. Implementation Quality Gates

### Development Phase Gates

- [ ] **Requirements Review** - All requirements are clear and testable
- [ ] **Design Review** - Architecture and design are approved
- [ ] **Code Review** - All code has been reviewed and approved
- [ ] **Testing Complete** - All tests pass with required coverage
- [ ] **Performance Validated** - Performance meets requirements
- [ ] **Security Reviewed** - Security implications considered and addressed

### Deployment Phase Gates

- [ ] **Documentation Complete** - All documentation is written and reviewed
- [ ] **User Training** - Team is trained on new workflow
- [ ] **Rollout Plan** - Gradual rollout strategy is defined
- [ ] **Monitoring Setup** - Metrics and alerting are configured
- [ ] **Rollback Plan** - Rollback procedures are documented

---

## 8. Acceptance Criteria

### Functional Acceptance Criteria
- [ ] 100% of bugfix PRs contain Bug Snapshot and Didn't Touch sections
- [ ] 95% of bugfix PRs include at least one test change (Repro or Guardrail)
- [ ] Cursor preset works with keyboard shortcut ⌘⌥B / Ctrl+Alt+B
- [ ] Hot-zone rules trigger appropriately for protected directories
- [ ] CI guard validates bugfix PRs and provides clear error messages
- [ ] Quick reference document is accessible and contains hotkey information

### Non-Functional Acceptance Criteria
- [ ] Preset injection completes in < 1 second
- [ ] CI validation completes in < 30 seconds
- [ ] Rule triggers display in < 500ms
- [ ] Documentation loads in < 2 seconds
- [ ] 99.9% CI check availability
- [ ] 99.5% preset reliability

### Business Acceptance Criteria
- [ ] Regression rate in hot zones drops ≥ 30% over 30 days
- [ ] Median time-to-fix unchanged or improved (≤ baseline ±10%)
- [ ] CI bugfix guard pass-rate ≥ 90% after week 2
- [ ] 80% developer adoption of playbook workflow
- [ ] 4.5/5 developer satisfaction rating

---

## 9. Risks & Mitigations

### Technical Risks
- **Alert Fatigue**: Too many nudges from hot-zone rules
  - *Mitigation*: Restrict rules to hot zones, keep rule text short
- **Ceremony Creep**: Process becomes too burdensome
  - *Mitigation*: Least-Diff principle + two-test model (Repro, one Guardrail)
- **Bypass with --no-verify**: Developers circumvent local hooks
  - *Mitigation*: CI backstop remains authoritative on PRs

### Operational Risks
- **Low Adoption**: Developers don't use the playbook
  - *Mitigation*: Start with soft enforcement, gather feedback, iterate
- **Performance Impact**: CI checks slow down PR process
  - *Mitigation*: Optimize check performance, run in parallel where possible
- **Maintenance Overhead**: Keeping playbook and rules updated
  - *Mitigation*: Version control, automated validation, clear ownership

### Business Risks
- **Velocity Impact**: Process slows down development
  - *Mitigation*: Focus on high-value areas, allow emergency overrides
- **Quality Regression**: Process doesn't improve outcomes
  - *Mitigation*: Measure outcomes, adjust process based on data
- **Team Resistance**: Developers reject new workflow
  - *Mitigation*: Involve team in design, provide training, gather feedback

---

## 10. Dependencies

### Technical Dependencies
- **Cursor IDE**: Support for presets and folder-specific rules
- **GitHub**: PR templates and CI/CD capabilities
- **Testing Framework**: Existing pytest infrastructure
- **Documentation System**: Markdown support and link validation

### Process Dependencies
- **Team Buy-in**: Developer acceptance of new workflow
- **Training**: Team education on playbook usage
- **Monitoring**: Metrics collection and analysis capabilities
- **Feedback Loop**: Process for gathering and acting on feedback

### External Dependencies
- **Cursor Updates**: Potential need for Cursor version updates
- **GitHub Features**: Reliance on GitHub PR and CI features
- **Documentation Tools**: Link checking and validation tools

---

## 11. Timeline

### Phase 1: Foundation (Days 0-1)
- [ ] Create `docs/004_bugfix_playbook.md`
- [ ] Create `docs/bugfix_playbook_quickref.md`
- [ ] Create Cursor preset `docs/cursor/presets/debug_playbook_preset.md`
- [ ] Announce keyboard shortcut (⌘⌥B / Ctrl+Alt+B)

### Phase 2: Enforcement (Days 1-2)
- [ ] Enable hot-zone rules for validator/vector_store/dashboard/archive
- [ ] Update PR template with bugfix sections
- [ ] Create CI guard `ci/bugfix-guard.sh`
- [ ] Educate team via PR example

### Phase 3: Validation (Days 2-7)
- [ ] Start CI guard in WARN mode (non-blocking)
- [ ] Monitor adoption and gather feedback
- [ ] Adjust rules and templates based on usage
- [ ] Prepare for hard enforcement

### Phase 4: Hard Enforcement (Days 7-14)
- [ ] Flip CI guard to BLOCK mode if signal is good
- [ ] Monitor compliance and quality metrics
- [ ] Implement optional commit/pre-commit hooks
- [ ] Review and adjust based on outcomes

### Phase 5: Optimization (Days 14-30)
- [ ] Analyze metrics and outcomes
- [ ] Optimize process based on data
- [ ] Expand to additional areas if successful
- [ ] Document lessons learned

---

## 12. Success Metrics

### Primary Metrics
- **Regression Rate**: Reduction in hot-zone regressions (target: ≥30%)
- **Test Coverage**: Percentage of bugfixes with tests (target: ≥95%)
- **Process Compliance**: Percentage of PRs following playbook (target: ≥90%)
- **Developer Satisfaction**: Survey rating (target: ≥4.5/5)

### Secondary Metrics
- **Time to Fix**: Median time for bug resolution (target: ≤baseline ±10%)
- **CI Pass Rate**: Percentage of bugfix PRs passing CI (target: ≥90%)
- **Adoption Rate**: Percentage of developers using playbook (target: ≥80%)
- **Error Reduction**: Reduction in production bugs (target: ≥20%)

### Leading Indicators
- **Preset Usage**: Frequency of playbook preset usage
- **Rule Triggers**: Number of hot-zone rule activations
- **Template Completion**: Percentage of PR template sections filled
- **Feedback Quality**: Quality and quantity of developer feedback

---

## 13. Open Questions

### Technical Questions
1. **Default Feature Flag Convention**: Should we establish a default feature flag convention for risky fixes (e.g., `FIX_<AREA>_ENABLED`)?
2. **Observability Requirements**: Should observability hooks (logs/metrics) be required for fixes touching public contracts?
3. **Rule Granularity**: How granular should hot-zone rules be? File-level vs. directory-level?
4. **CI Performance**: What's the acceptable performance impact of CI checks on PR velocity?

### Process Questions
1. **Emergency Override**: What constitutes a "critical outage" that justifies emergency override?
2. **Escalation Criteria**: When should a bugfix be escalated to the full 5-phase framework?
3. **Training Approach**: What's the best approach for training the team on the new workflow?
4. **Feedback Collection**: How should we collect and act on developer feedback?

### Business Questions
1. **Success Definition**: What's the minimum acceptable improvement in regression rate?
2. **Rollback Criteria**: Under what conditions should we rollback the enforcement?
3. **Expansion Scope**: Which additional areas should be considered for hot-zone protection?
4. **Resource Allocation**: What level of ongoing maintenance is acceptable?

---

## 14. Change Log

### Version 1.0 (Initial Release)
- **Added**: `docs/004_bugfix_playbook.md` - Global bug-fix playbook
- **Added**: `docs/bugfix_playbook_quickref.md` - Quick reference with hotkey
- **Added**: `docs/cursor/presets/debug_playbook_preset.md` - Cursor preset
- **Added**: Hot-zone rules for fragile modules
- **Updated**: PR template with bugfix sections
- **Added**: `ci/bugfix-guard.sh` - CI validation
- **Added**: Optional commit/pre-commit tooling

### Future Versions
- **v1.1**: Enhanced metrics and monitoring
- **v1.2**: Additional hot-zone coverage
- **v1.3**: Advanced automation features
- **v2.0**: Integration with broader governance framework

---

## 15. References

### Related Documents
- `000_core/000_backlog.md` - Current backlog and priorities
- `400_guides/400_comprehensive-coding-best-practices.md` - Coding standards
- `400_guides/400_testing-strategy-guide.md` - Testing approach
- `400_guides/400_security-best-practices-guide.md` - Security requirements

### External References
- [Cursor Documentation](https://cursor.sh/docs) - IDE capabilities
- [GitHub PR Templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository) - PR template guidelines
- [GitHub Actions](https://docs.github.com/en/actions) - CI/CD capabilities

---

## 16. Appendices

### Appendix A: Playbook Template
Full playbook template with all sections and examples

### Appendix B: Cursor Configuration
Detailed Cursor preset and rule configuration

### Appendix C: CI Configuration
Complete CI guard script and GitHub Actions configuration

### Appendix D: Training Materials
Developer training materials and examples

---

**Document Version**: 1.0
**Last Updated**: Current Date
**Owner**: Development Team
**Reviewers**: To be assigned
**Approval Status**: Pending
