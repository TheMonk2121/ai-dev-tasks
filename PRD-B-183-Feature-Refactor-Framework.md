# PRD: Feature Refactor Framework (Initial Draft → Consensus → Validation)

**Backlog Item**: B-183
**Status**: Ready for Implementation
**Estimated Hours**: 5 hours

**Dependencies**:
- **Upstream**: B-182 (Bug-Fix Playbook must be implemented first)
- **Downstream**: Future architectural changes, governance improvements, framework enhancements
- **Blocking**: None

**Impact Scope**:
- **Direct**: Refactor workflow, consensus process, CI validation, PR templates
- **Indirect**: All future refactors, architectural decisions, governance maturity
- **Public Contracts**: May affect system architecture and design patterns

## TL;DR

**What**: Introduce a Feature Refactor Framework for structural/systemic changes that go beyond bug fixes, using a 5-phase consensus method with progressive enforcement.

**Why**: Refactors are high-risk and can't be handled with "surgical speed" like bugfixes. They require deliberate consensus to prevent "silent refactors" from landing without stakeholder review.

**How**: 5-phase framework (Initial Draft → Red/Blue Reviews → Consensus → Validation) with unified PR template, enhanced CI guard with Conventional Commits validation, and integration with existing 000→003 governance.

**Impact**: Prevent architectural drift, ensure stakeholder consensus, maintain velocity through progressive enforcement.

---

## 1. Problem Statement

### Current State
- Refactors are high-risk changes that alter contracts, abstractions, or performance
- No clear escalation path when bugfix playbook (004) is insufficient
- "Silent refactors" can land without stakeholder review
- No structured approach for consensus-driven architectural changes

### Pain Points
- Unclear when to use bugfix vs refactor vs full PRD workflow
- Refactors lack systematic stakeholder input
- Architecture decisions aren't properly documented
- No validation that refactors achieve their intended goals

### Root Cause
- Missing middle ground between surgical bugfixes and full governance
- No structured consensus process for architectural changes
- Lack of integration with existing governance framework

---

## 2. Solution Overview

### High-Level Solution
A 5-phase consensus framework for refactors that provides structured stakeholder input while maintaining velocity:

1. **Initial Draft** - Capture the change intent and scope
2. **Red/Blue Reviews** - Surface risks and support points
3. **Consensus Feedback** - Refine based on stakeholder input
4. **Validation Checkpoint** - Decide and record outcomes
5. **Integration** - Connect with existing 000→003 governance

### Key Features
- **Clear Scope Gate** - Binary decision: bugfix (004) vs refactor (005)
- **5-Phase Consensus** - Structured stakeholder input process
- **Unified PR Template** - Single template with conditional sections
- **Enhanced CI Guard** - Conventional Commits validation with framework compliance
- **Progressive Enforcement** - WARN → BLOCK based on adoption
- **Integration Points** - Connect with existing governance workflow

### Technical Approach
- **Documentation-First** - Markdown-based playbook with clear structure
- **Cursor Integration** - Preset for running consensus phases
- **CI/CD Integration** - GitHub Actions for validation
- **Progressive Rollout** - Soft enforcement → monitoring → hard enforcement

### Integration Points
- **000 Backlog** - Refactor items tracked with consensus scores
- **001 PRD** - Public contract changes require full PRD
- **002 Tasks** - Refactor tasks include consensus validation
- **003 Execution** - Refactor execution references consensus decisions

---

## 3. Functional Requirements

### User Stories

#### US-001: Developer Determines Framework to Use
**As a** developer making changes
**I want to** clearly understand when to use bugfix vs refactor vs PRD framework
**So that** I choose the appropriate level of rigor for my change

**Acceptance Criteria**:
- Decision matrix clearly shows which framework applies
- Scope gate provides clear escalation path
- Integration with existing governance is documented

#### US-002: Developer Runs Refactor Consensus Process
**As a** developer proposing a refactor
**I want to** use a structured 5-phase consensus process
**So that** I get stakeholder input and validation before proceeding

**Acceptance Criteria**:
- Cursor preset guides through all 5 phases
- Max 3 rounds enforced to maintain velocity
- Clear decision (PASS/FAIL) at end of process

#### US-003: PR Template Adapts to Change Type
**As a** developer creating a PR
**I want to** see relevant sections based on change type
**So that** I provide appropriate documentation without overhead

**Acceptance Criteria**:
- Single PR template with conditional sections
- Bugfix sections show for bugfix PRs
- Refactor sections show for refactor PRs
- Template is clear and easy to use

#### US-004: CI Validates Framework Requirements
**As a** developer submitting a PR
**I want** automated validation based on my commit message
**So that** the appropriate framework is enforced consistently

**Acceptance Criteria**:
- CI validates commit message prefixes (fix:, refactor:, feat:)
- CI enforces appropriate framework sections based on commit type
- CI provides clear error messages for framework violations
- CI maintains performance (<30 seconds)

#### US-005: Framework Quick-Reference Guides Selection
**As a** developer choosing a framework
**I want to** quickly understand which framework applies to my change
**So that** I use the right level of rigor without confusion

**Acceptance Criteria**:
- Framework decision matrix is clear and accessible
- Quick reference shows commit prefixes and frameworks
- Reference includes keyboard shortcuts and commands
- Reference is easily discoverable and up-to-date

### Feature Specifications

#### Decision Matrix
```
| Change Type | Framework | Time | Rigor | When to Use |
|-------------|-----------|------|-------|-------------|
| Bug fix | 004 Bug-Fix | 1 day | Surgical | Isolated fixes, no contract changes |
| Internal refactor | 005 Refactor | 1 week | Consensus | Multiple modules, new patterns |
| Public contract change | 001 PRD | 2 weeks | Full governance | APIs, schemas, public interfaces |
```

#### Scope Gate Criteria
Use Refactor Framework (005) if:
- Change alters public contracts (APIs, schemas, events)
- Change affects multiple modules (not isolated)
- Change introduces new abstractions/patterns
- Change has systemic performance or scale impact

If none apply → default to Bugfix Playbook (004)

#### 5-Phase Consensus Structure
```
Phase 1: Initial Draft
- Title, proposer, context, description
- Assumptions, constraints, success criteria

Phase 2: Red Review
- Critiques, risks, alternatives, challenge questions
- Severity score (0.0-1.0)

Phase 3: Blue Review
- Support points, enhancement suggestions, implementation guidance
- Confidence score (0.0-1.0)

Phase 4: Consensus Feedback
- Feedback & refinements
- Consensus score (avg of Red/Blue + participants)
- Next steps

Phase 5: Validation Checkpoint
- Criteria met vs failed
- Decision: Pass/Fail
- Priority & timeline
- Risk mitigation & success metrics
```

#### Unified PR Template Structure
```markdown
## Type
- [ ] Feature
- [ ] Bugfix
- [x] Refactor
- [ ] Chore

<!-- Bugfix sections (conditional) -->
{{#if bugfix}}
## Bug Snapshot
Bugfix sections
{{/if}}

<!-- Refactor sections (conditional) -->
{{#if refactor}}
## Refactor Consensus Framework
Phase 1-5 sections
{{/if}}
```

#### CI Guard Logic
- **Trigger**: Commit message prefixes (fix:, refactor:, feat:)
- **Validation**: Appropriate framework sections based on commit type
- **Enforcement**: Framework compliance based on Conventional Commits
- **Output**: Clear pass/fail with actionable error messages
- **Performance**: Complete within 30 seconds

### Data Requirements
- **Consensus Tracking**: Track consensus scores and decisions
- **Integration Data**: Link refactors to backlog items and PRDs
- **Adoption Metrics**: Monitor framework usage and effectiveness
- **Validation Outcomes**: Track refactor success rates

### API Requirements
- **Cursor API**: Integration with Cursor preset system
- **GitHub API**: PR template and CI check integration
- **File System**: Read/write access for documentation

---

## 4. Non-Functional Requirements

### Performance Requirements
- **Preset Response Time**: < 1 second for preset injection
- **CI Check Duration**: < 30 seconds for validation
- **Template Load Time**: < 2 seconds for PR template
- **Consensus Process**: Complete within 3 rounds max

### Security Requirements
- **Input Validation**: Sanitize all user inputs in PR templates
- **Access Control**: Ensure only authorized users can modify playbook
- **Audit Trail**: Log all consensus decisions and outcomes
- **Secure Storage**: Protect sensitive architectural information

### Reliability Requirements
- **CI Check Uptime**: 99.9% availability for refactor validation
- **Preset Reliability**: 99.5% success rate for preset injection
- **Template Consistency**: Consistent behavior across different environments
- **Error Handling**: Graceful degradation when components fail

### Usability Requirements
- **Decision Clarity**: Clear guidance on which framework to use
- **Process Simplicity**: Easy to follow 5-phase process
- **Error Messages**: Clear, actionable feedback for failures
- **Integration**: Seamless connection with existing workflows

---

## 5. Testing Strategy

### Test Coverage Goals
- **Unit Tests**: 90% coverage for CI guard logic
- **Integration Tests**: 85% coverage for Cursor integration
- **End-to-End Tests**: 80% coverage for complete workflow
- **Documentation Tests**: 100% coverage for link validation

### Testing Phases
1. **Unit Testing**: Individual component validation
2. **Integration Testing**: Cursor preset and CI integration
3. **System Testing**: End-to-end workflow validation
4. **Acceptance Testing**: User acceptance validation

### Automation Requirements
- **Automated**: CI guard logic, preset validation, template testing
- **Manual**: User experience testing, consensus process validation
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
- **Template Processing**: < 2 seconds load time
- **Consensus Process**: ≤ 3 rounds maximum

### Security Validation
- Input sanitization for all user-provided content
- Secure handling of architectural information
- Proper access controls for playbook modifications
- Audit logging for all consensus decisions

### User Acceptance Criteria
- **Usability**: 95% of developers can use framework without training
- **Adoption**: 80% of refactor PRs follow consensus process
- **Compliance**: 90% of refactors complete within 3 rounds
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
- [ ] **Rollout Plan** - Progressive rollout strategy is defined
- [ ] **Monitoring Setup** - Metrics and alerting are configured
- [ ] **Rollback Plan** - Rollback procedures are documented

---

## 8. Acceptance Criteria

### Functional Acceptance Criteria
- [ ] Decision matrix clearly guides framework selection
- [ ] 100% of refactor PRs have all 5 consensus phases
- [ ] Consensus decisions reached in ≤ 3 rounds
- [ ] CI guard validates refactor requirements
- [ ] Integration with existing governance works seamlessly

### Non-Functional Acceptance Criteria
- [ ] Preset injection completes in < 1 second
- [ ] CI validation completes in < 30 seconds
- [ ] Template loads in < 2 seconds
- [ ] Consensus process completes in ≤ 3 rounds
- [ ] 99.9% CI check availability

### Business Acceptance Criteria
- [ ] 80% adoption rate of refactor framework
- [ ] 90% refactor success rate (achieve intended goals)
- [ ] Consensus time ≤ 3 days average
- [ ] 4.5/5 developer satisfaction rating
- [ ] Zero "silent refactors" bypassing consensus

---

## 9. Risks & Mitigations

### Technical Risks
- **Template Complexity**: Unified template becomes unwieldy
  - *Mitigation*: Keep conditional sections simple, test thoroughly
- **CI Performance**: Guard slows down PR process
  - *Mitigation*: Optimize check performance, run in parallel
- **Integration Issues**: Framework doesn't connect with existing governance
  - *Mitigation*: Explicit integration points, thorough testing

### Operational Risks
- **Low Adoption**: Developers don't use the framework
  - *Mitigation*: Progressive enforcement, gather feedback, iterate
- **Process Overhead**: Consensus becomes too burdensome
  - *Mitigation*: 3-round limit, clear timeboxes, lightweight process
- **Scope Creep**: Framework used for simple changes
  - *Mitigation*: Clear scope gate, decision matrix, training

### Business Risks
- **Velocity Impact**: Process slows down development
  - *Mitigation*: Progressive rollout, emergency override, clear timeboxes
- **Quality Regression**: Process doesn't improve outcomes
  - *Mitigation*: Measure outcomes, adjust process based on data
- **Team Resistance**: Developers reject new workflow
  - *Mitigation*: Involve team in design, provide training, gather feedback

---

## 10. Dependencies

### Technical Dependencies
- **Cursor IDE**: Support for presets and conditional templates
- **GitHub**: PR templates and CI/CD capabilities
- **Testing Framework**: Existing pytest infrastructure
- **Documentation System**: Markdown support and link validation

### Process Dependencies
- **Team Buy-in**: Developer acceptance of new workflow
- **Training**: Team education on framework usage
- **Monitoring**: Metrics collection and analysis capabilities
- **Feedback Loop**: Process for gathering and acting on feedback

### External Dependencies
- **Cursor Updates**: Potential need for Cursor version updates
- **GitHub Features**: Reliance on GitHub PR and CI features
- **Documentation Tools**: Link checking and validation tools

---

## 11. Timeline

### Phase 1: Foundation (Days 0-1)
- [ ] Create `docs/005_feature_refactor_playbook.md`
- [ ] Create Cursor preset `docs/cursor/presets/refactor_consensus_preset.md`
- [ ] Update unified PR template with conditional sections
- [ ] Create CI guard `ci/refactor-guard.sh`

### Phase 2: Soft Enforcement (Days 1-7)
- [ ] Configure CI guard in WARN mode (non-blocking)
- [ ] Trial with one refactor PR
- [ ] Monitor adoption and gather feedback
- [ ] Adjust process based on usage

### Phase 3: Hard Enforcement (Days 7-14)
- [ ] Monitor adoption rate
- [ ] If adoption ≥80%, flip CI guard to BLOCK mode
- [ ] If adoption <80%, extend soft enforcement period
- [ ] Document lessons learned

### Phase 4: Optimization (Days 14-30)
- [ ] Analyze metrics and outcomes
- [ ] Optimize process based on data
- [ ] Expand integration with existing governance
- [ ] Document best practices

---

## 12. Success Metrics

### Primary Metrics
- **Adoption Rate**: Percentage of refactors using framework (target: ≥80%)
- **Success Rate**: Percentage of refactors achieving goals (target: ≥90%)
- **Consensus Time**: Average time to reach consensus (target: ≤3 days)
- **Developer Satisfaction**: Survey rating (target: ≥4.5/5)

### Secondary Metrics
- **CI Pass Rate**: Percentage of refactor PRs passing CI (target: ≥95%)
- **Round Count**: Average consensus rounds per refactor (target: ≤2.5)
- **Integration Success**: Percentage of refactors properly integrated (target: ≥95%)
- **Zero Silent Refactors**: No refactors bypassing consensus (target: 100%)

### Leading Indicators
- **Preset Usage**: Frequency of consensus preset usage
- **Template Completion**: Percentage of PR template sections filled
- **Stakeholder Participation**: Number of participants in consensus process
- **Feedback Quality**: Quality and quantity of stakeholder feedback

---

## 13. Open Questions

### Technical Questions
1. **Template Complexity**: How complex can conditional sections be before they become unwieldy?
2. **CI Performance**: What's the acceptable performance impact of CI checks on PR velocity?
3. **Integration Depth**: How deeply should refactors integrate with existing governance?
4. **Emergency Override**: What constitutes a "critical refactor" that justifies emergency override?

### Process Questions
1. **Stakeholder Definition**: Who should participate in consensus for different types of refactors?
2. **Timeboxing**: Should each phase have explicit time limits?
3. **Escalation Criteria**: When should a refactor be escalated to full PRD workflow?
4. **Feedback Collection**: How should we collect and act on stakeholder feedback?

### Business Questions
1. **Success Definition**: What's the minimum acceptable adoption rate?
2. **Rollback Criteria**: Under what conditions should we rollback the framework?
3. **Expansion Scope**: Which additional change types should use this framework?
4. **Resource Allocation**: What level of ongoing maintenance is acceptable?

---

## 14. Change Log

### Version 1.0 (Initial Release)
- **Added**: `docs/005_feature_refactor_playbook.md` - Refactor consensus framework
- **Added**: `docs/cursor/presets/refactor_consensus_preset.md` - Cursor preset
- **Updated**: Unified PR template with conditional sections
- **Added**: `ci/refactor-guard.sh` - CI validation
- **Added**: Integration points with existing governance

### Future Versions
- **v1.1**: Enhanced metrics and monitoring
- **v1.2**: Additional integration features
- **v1.3**: Advanced automation features
- **v2.0**: Integration with broader governance framework

---

## 15. References

### Related Documents
- `000_core/000_backlog.md` - Current backlog and priorities
- `PRD-B-182-Global-Bug-Fix-Playbook.md` - Bugfix framework
- `400_guides/400_comprehensive-coding-best-practices.md` - Coding standards
- `400_guides/400_testing-strategy-guide.md` - Testing approach

### External References
- [Cursor Documentation](https://cursor.sh/docs) - IDE capabilities
- [GitHub PR Templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository) - PR template guidelines
- [GitHub Actions](https://docs.github.com/en/actions) - CI/CD capabilities

---

## 16. Appendices

### Appendix A: Decision Matrix
Complete decision matrix with examples
### Appendix B: Consensus Process Examples
Real-world examples of consensus process
### Appendix C: Integration Points
Detailed integration with existing governance
### Appendix D: Training Materials
Developer training materials and examples
---

**Document Version**: 1.0
**Last Updated**: Current Date
**Owner**: Development Team
**Reviewers**: To be assigned
**Approval Status**: Pending
