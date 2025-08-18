# B-182: Global Bug-Fix Playbook + Enforcement Layers - Task List

## Overview
**PRD**: `PRD-B-182-Global-Bug-Fix-Playbook.md`
**Priority**: High (5 points)
**Estimated Total Time**: 4 hours (MVP with enhanced rules)
**Dependencies**: None

## MVP Implementation (1 day, 4 hours)

### Task 1.1: Create Global Bug-Fix Playbook Documentation
**Priority**: Critical
**Estimated Time**: 1 hour
**Dependencies**: None

**Description**: Create the core bug-fix playbook documentation that serves as the source of truth for the debugging workflow.

**Acceptance Criteria**:
- [ ] `docs/004_bugfix_playbook.md` exists with complete playbook structure
- [ ] Playbook includes Problem Snapshot, Dual Review, and Resolution Check sections
- [ ] Emergency override and closure ritual sections are documented
- [ ] Principles (Least-Diff, Contracts First, Tests Prove It) are clearly stated
- [ ] Document follows markdown standards and includes TL;DR section

**Testing Requirements**:
- [ ] **Documentation Tests**: Link validation passes
- [ ] **Content Tests**: All sections are complete and properly formatted
- [ ] **Accessibility Tests**: Document is readable and well-structured

**Implementation Notes**:
- Use the playbook structure defined in the PRD
- Include examples for each section
- Ensure compatibility with existing documentation standards

**Quality Gates**:
- [ ] **Content Review**: Documentation reviewed for completeness and clarity
- [ ] **Format Validation**: Markdown linting passes
- [ ] **Link Check**: All internal links are valid

---

### Task 1.2: Create Quick Reference Documentation
**Priority**: Critical
**Estimated Time**: 30 minutes
**Dependencies**: Task 1.1

**Description**: Create a quick reference document that provides easy access to the playbook hotkey and essential information.

**Acceptance Criteria**:
- [ ] `docs/bugfix_playbook_quickref.md` exists
- [ ] Document includes preset name "Run Bug-Fix Playbook"
- [ ] Keyboard shortcut ⌘⌥B (macOS) / Ctrl+Alt+B (Windows/Linux) is documented
- [ ] Links to all related files (playbook, preset, rules, templates) are provided
- [ ] Mini prompt template is included for copy/paste use

**Testing Requirements**:
- [ ] **Link Tests**: All referenced files exist and are accessible
- [ ] **Content Tests**: Hotkey information is accurate and complete

**Implementation Notes**:
- Focus on discoverability and ease of use
- Include troubleshooting section for common issues

**Quality Gates**:
- [ ] **Usability Review**: Document is easy to find and use
- [ ] **Accuracy Check**: All hotkeys and paths are correct

---

### Task 1.3: Create Cursor Chat Preset
**Priority**: Critical
**Estimated Time**: 1 hour
**Dependencies**: Task 1.1

**Description**: Create a Cursor chat preset that injects the structured bug-fix playbook prompt.

**Acceptance Criteria**:
- [ ] `docs/cursor/presets/debug_playbook_preset.md` exists
- [ ] Preset includes role definition "You are a senior debugging assistant"
- [ ] Structured prompt with all required sections is included
- [ ] Clear instructions for minimal diff and guardrail test are provided
- [ ] Self-review requirements for regressions/security are documented

**Testing Requirements**:
- [ ] **Preset Tests**: Preset can be imported into Cursor successfully
- [ ] **Content Tests**: All sections are properly formatted and complete
- [ ] **Integration Tests**: Preset works with Cursor's chat interface

**Implementation Notes**:
- Test preset in actual Cursor environment
- Ensure proper markdown formatting for Cursor compatibility

**Quality Gates**:
- [ ] **Functionality Test**: Preset works correctly in Cursor
- [ ] **Content Review**: All sections are complete and actionable

---

### Task 1.2: Create Enhanced Hot-Zone Cursor Rules (Multi-Framework Aware)
**Priority**: High
**Estimated Time**: 1.5 hours
**Dependencies**: Task 1.1

**Description**: Create hot-zone rules that guide developers to appropriate frameworks based on commit messages.

**Acceptance Criteria**:
- [ ] Rules exist for `src/validator/**`, `src/vector_store/**`, `src/dashboard/**`, `scripts/archive_*.py`
- [ ] Rules detect commit message prefixes (fix:, refactor:, feat:)
- [ ] Rules suggest appropriate framework (004, 005, 001-003) based on commit type
- [ ] Rules provide clear guidance without being intrusive


**Testing Requirements**:
- [ ] **Rule Tests**: Rules trigger appropriately for protected directories
- [ ] **Content Tests**: Rule text is clear and actionable
- [ ] **Integration Tests**: Rules work with Cursor's rule system

**Implementation Notes**:
- Create separate rule files for each protected directory
- Test rules in actual Cursor environment
- Ensure rules don't interfere with normal development

**Quality Gates**:
- [ ] **Functionality Test**: Rules trigger correctly
- [ ] **Usability Review**: Rules are helpful without being intrusive

---

### Task 1.3: Create CI Guard Script
**Priority**: High
**Estimated Time**: 1 hour
**Dependencies**: None

**Description**: Enhance the GitHub PR template to include mandatory bugfix documentation sections.

**Acceptance Criteria**:
- [ ] PR template includes "Bug Snapshot" section
- [ ] Template requires "Didn't Touch" and "Blast Radius" documentation
- [ ] Template enforces test plan documentation
- [ ] Template is automatically applied to bugfix PRs
- [ ] Template includes Type selection (Feature/Bugfix/Chore)

**Testing Requirements**:
- [ ] **Template Tests**: Template renders correctly in GitHub
- [ ] **Content Tests**: All sections are properly formatted
- [ ] **Integration Tests**: Template applies to new PRs

**Implementation Notes**:
- Update `.github/pull_request_template.md`
- Ensure compatibility with existing template structure
- Test template in GitHub environment

**Quality Gates**:
- [ ] **Template Review**: Template is complete and user-friendly
- [ ] **GitHub Test**: Template works correctly in GitHub interface

---

### Task 2.3: Create CI Guard Script
**Priority**: High
**Estimated Time**: 1.5 hours
**Dependencies**: Task 2.2

**Description**: Create a CI script that validates bugfix PR requirements.

**Acceptance Criteria**:
- [ ] `ci/bugfix-guard.sh` exists and is executable
- [ ] Script runs on bugfix/hotfix labeled PRs
- [ ] Script validates presence of "Bug Snapshot" section
- [ ] Script requires at least one test file change
- [ ] Script provides clear error messages for failures

**Testing Requirements**:
- [ ] **Unit Tests**: Script logic is tested with various inputs
- [ ] **Integration Tests**: Script works with GitHub Actions
- [ ] **Error Tests**: Script handles edge cases and errors gracefully
- [ ] **Performance Tests**: Script completes within 30 seconds

**Implementation Notes**:
- Use bash for compatibility
- Include proper error handling and logging
- Test with sample PR data

**Quality Gates**:
- [ ] **Code Review**: Script is reviewed for security and reliability
- [ ] **Test Coverage**: All script logic is tested
- [ ] **Performance Test**: Script meets performance requirements

---

## Phase 3: Validation (Days 2-7)

### Task 3.1: Configure CI Guard in WARN Mode
**Priority**: Medium
**Estimated Time**: 30 minutes
**Dependencies**: Task 2.3

**Description**: Configure the CI guard to run in warning mode (non-blocking) for initial testing.

**Acceptance Criteria**:
- [ ] CI guard is configured in GitHub Actions
- [ ] Guard runs in WARN mode (non-blocking)
- [ ] Guard provides feedback without blocking merges
- [ ] Guard logs are accessible and informative

**Testing Requirements**:
- [ ] **CI Tests**: Guard runs successfully in GitHub Actions
- [ ] **Log Tests**: Guard provides useful feedback
- [ ] **Integration Tests**: Guard integrates with existing CI pipeline

**Implementation Notes**:
- Configure as GitHub Action workflow
- Ensure proper error handling and logging
- Monitor for false positives

**Quality Gates**:
- [ ] **CI Review**: Guard integrates properly with existing CI
- [ ] **Monitoring Setup**: Guard logs are monitored and accessible

---

### Task 3.2: Create Training and Documentation
**Priority**: Medium
**Estimated Time**: 1 hour
**Dependencies**: Tasks 1.1, 1.2, 1.3, 2.1, 2.2

**Description**: Create training materials and documentation for the team.

**Acceptance Criteria**:
- [ ] Training materials explain the new workflow
- [ ] Documentation includes examples and best practices
- [ ] Team is educated on keyboard shortcuts and rules
- [ ] FAQ section addresses common questions

**Testing Requirements**:
- [ ] **Content Tests**: Training materials are complete and accurate
- [ ] **Usability Tests**: Materials are easy to understand and follow

**Implementation Notes**:
- Create both written and video documentation
- Include troubleshooting guide
- Provide examples of good and bad implementations

**Quality Gates**:
- [ ] **Content Review**: Training materials are reviewed for accuracy
- [ ] **Usability Test**: Materials are tested with team members

---

## Phase 4: Hard Enforcement (Days 7-14)

### Task 4.1: Flip CI Guard to BLOCK Mode
**Priority**: High
**Estimated Time**: 30 minutes
**Dependencies**: Task 3.1

**Description**: Switch CI guard from WARN to BLOCK mode after validation period.

**Acceptance Criteria**:
- [ ] CI guard blocks PRs that don't meet requirements
- [ ] Guard provides clear error messages
- [ ] Guard maintains 99.9% availability
- [ ] Rollback plan is documented and tested

**Testing Requirements**:
- [ ] **Blocking Tests**: Guard correctly blocks non-compliant PRs
- [ ] **Error Tests**: Guard provides helpful error messages
- [ ] **Rollback Tests**: Rollback procedure works correctly

**Implementation Notes**:
- Monitor for false positives during transition
- Have rollback plan ready
- Communicate change to team

**Quality Gates**:
- [ ] **Monitoring Review**: Guard performance is monitored
- [ ] **Team Communication**: Change is communicated to team

---

### Task 4.2: Implement Optional Commit/Pre-commit Hooks
**Priority**: Low
**Estimated Time**: 1 hour
**Dependencies**: Task 4.1

**Description**: Create optional commit templates and pre-commit hooks for additional enforcement.

**Acceptance Criteria**:
- [ ] `.gitmessage-bugfix.txt` commit template exists
- [ ] Pre-commit hook checks for test changes on bugfix commits
- [ ] Hooks are optional and can be bypassed with justification
- [ ] Hooks provide clear error messages

**Testing Requirements**:
- [ ] **Hook Tests**: Pre-commit hooks work correctly
- [ ] **Template Tests**: Commit template is properly formatted
- [ ] **Bypass Tests**: Hooks can be bypassed when needed

**Implementation Notes**:
- Make hooks optional to avoid blocking legitimate work
- Provide clear documentation on when to bypass
- Test with various commit scenarios

**Quality Gates**:
- [ ] **Hook Review**: Hooks are reviewed for reliability
- [ ] **Documentation Review**: Bypass procedures are documented

---

## Phase 5: Optimization (Days 14-30)

### Task 5.1: Analyze Metrics and Outcomes
**Priority**: Medium
**Estimated Time**: 2 hours
**Dependencies**: Task 4.1

**Description**: Collect and analyze metrics to measure the effectiveness of the bug-fix playbook.

**Acceptance Criteria**:
- [ ] Regression rate metrics are collected and analyzed
- [ ] Test coverage metrics are tracked
- [ ] Developer satisfaction is measured
- [ ] Process compliance rates are monitored
- [ ] Report is generated with recommendations

**Testing Requirements**:
- [ ] **Data Tests**: Metrics collection is accurate and complete
- [ ] **Analysis Tests**: Analysis provides actionable insights

**Implementation Notes**:
- Use existing monitoring infrastructure where possible
- Create automated reporting
- Focus on actionable metrics

**Quality Gates**:
- [ ] **Data Review**: Metrics are accurate and meaningful
- [ ] **Analysis Review**: Analysis provides useful insights

---

### Task 5.2: Optimize Process Based on Data
**Priority**: Medium
**Estimated Time**: 1 hour
**Dependencies**: Task 5.1

**Description**: Optimize the bug-fix playbook process based on collected metrics and feedback.

**Acceptance Criteria**:
- [ ] Process improvements are identified and implemented
- [ ] Documentation is updated with lessons learned
- [ ] Rules and templates are refined based on usage data
- [ ] Team feedback is incorporated

**Testing Requirements**:
- [ ] **Improvement Tests**: Improvements are tested and validated
- [ ] **Documentation Tests**: Updates are complete and accurate

**Implementation Notes**:
- Focus on high-impact, low-effort improvements
- Maintain backward compatibility
- Document all changes

**Quality Gates**:
- [ ] **Improvement Review**: Changes are reviewed and approved
- [ ] **Documentation Update**: All changes are documented

---

## Quality Gates Summary

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

## Success Metrics

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

## Risk Mitigation

### Technical Risks
- **Alert Fatigue**: Restrict rules to hot zones, keep rule text short
- **Ceremony Creep**: Least-Diff principle + two-test model
- **Bypass with --no-verify**: CI backstop remains authoritative

### Operational Risks
- **Low Adoption**: Start with soft enforcement, gather feedback, iterate
- **Performance Impact**: Optimize check performance, run in parallel
- **Maintenance Overhead**: Version control, automated validation, clear ownership

### Business Risks
- **Velocity Impact**: Focus on high-value areas, allow emergency overrides
- **Quality Regression**: Measure outcomes, adjust process based on data
- **Team Resistance**: Involve team in design, provide training, gather feedback

---

**Task List Version**: 1.0
**Last Updated**: Current Date
**Owner**: Development Team
**Reviewers**: To be assigned
**Approval Status**: Pending
