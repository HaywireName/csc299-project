<!--
Sync Impact Report:
Version: 1.0.0 → 1.1.0 (Documentation merge requirement)
Last Amended: 2025-11-17
Modified Sections:
  - Code Review Requirements: Added user documentation merge gate
  - Quality Checklist: Added user documentation verification
  - Development Workflow: Clarified documentation must be complete before master merge
Added Requirements:
  - User documentation MUST be created and up-to-date before merging to master
  - Documentation review mandatory in code review process
Templates Status:
  ✅ spec-template.md - Already requires documentation
  ✅ plan-template.md - Aligns with documentation requirements
  ✅ tasks-template.md - Aligns with documentation standards
Follow-up TODOs: None
-->

# Spec-Kit Constitution

## Core Principles

### I. Code Clarity & Simplicity (NON-NEGOTIABLE)

**Code MUST be self-documenting and immediately understandable.**

- Variable, function, and class names MUST clearly express their purpose without requiring comments
- Functions MUST do one thing and do it well (Single Responsibility Principle)
- Cyclomatic complexity MUST remain low - refactor when complexity exceeds reasonable thresholds
- Comments MUST explain "why", not "what" - the code itself explains "what"
- Avoid clever tricks - prefer explicit, boring code that anyone can understand
- YAGNI (You Aren't Gonna Need It) - implement only what is required NOW, not what might be needed later
- Maximum function/method length: 50 lines (exceptions MUST be justified in code review)
- Maximum file length: 500 lines (exceptions MUST be justified in complexity tracking)

**Rationale**: Maintainability and team velocity depend on code that can be understood by any team member without archaeology. Simple code has fewer bugs, is easier to test, and reduces cognitive load.

### II. Code Quality Standards (NON-NEGOTIABLE)

**All code MUST meet quality gates before merge.**

- Static analysis tools MUST run on every commit (linters, formatters, type checkers)
- Zero tolerance for linter warnings - fix or explicitly suppress with justification
- Type safety MUST be enforced where language supports it (TypeScript strict mode, Python type hints, etc.)
- Code coverage MUST be measured and maintained (minimum threshold: 80% for new code)
- Dead code MUST be removed - no commented-out code blocks
- Dependencies MUST be pinned to specific versions and regularly audited for security vulnerabilities
- Every public API MUST have documentation (docstrings, JSDoc, etc.)
- Code review MUST be completed by at least one other team member before merge

**Quality Checklist (MUST pass before merge)**:
- [ ] Linter passes with zero warnings
- [ ] Type checker passes (if applicable)
- [ ] Tests pass (all existing + new tests)
- [ ] Code coverage meets minimum threshold
- [ ] Documentation updated (if API changes)
- [ ] User documentation created and up-to-date (required before merge to master)
- [ ] No debug code, console.log, or TODO comments without linked issues

**Rationale**: Quality gates catch bugs early, enforce consistency, and ensure code meets team standards automatically. Automated quality checks reduce review burden and prevent technical debt accumulation.

### III. Testing Standards (NON-NEGOTIABLE)

**Tests MUST exist before implementation and MUST fail before code is written.**

**Test-First Development Cycle**:
1. Write test cases based on acceptance criteria (tests MUST fail initially)
2. Implement minimal code to make tests pass (Red-Green-Refactor)
3. Refactor for clarity and simplicity while keeping tests green
4. Run full test suite to ensure no regressions

**Testing Hierarchy** (all applicable levels MUST be covered):
- **Contract Tests**: MUST exist for all public APIs, library interfaces, and service boundaries
- **Integration Tests**: MUST exist for multi-component workflows and user journeys
- **Unit Tests**: SHOULD exist for complex business logic and edge cases (optional for trivial code)

**Test Quality Requirements**:
- Tests MUST be deterministic (no flaky tests - fix or remove)
- Tests MUST be independent (no order dependencies)
- Tests MUST be fast (slow tests go in separate integration suite)
- Test names MUST clearly describe what is being tested and expected outcome
- Tests MUST use Given-When-Then structure or equivalent clarity
- Mock/stub external dependencies in unit tests (real dependencies in integration tests)

**Testing Workflow**:
- Tests are OPTIONAL unless explicitly required in feature specification
- When tests are required, they MUST be written first and fail before implementation
- All tests MUST pass before code review
- CI pipeline MUST run full test suite on every pull request

**Rationale**: Test-first development ensures code is testable by design, validates requirements are understood, and provides living documentation of system behavior. Failed-first tests prove tests actually test something.

### IV. User Experience Consistency (NON-NEGOTIABLE)

**User-facing interfaces MUST be consistent, predictable, and documented.**

**CLI/API Consistency**:
- Input/output formats MUST be consistent across all commands/endpoints
- Error messages MUST be actionable (tell users what to do next)
- Text-based I/O: stdin/args → stdout (data), stderr (errors)
- Support both machine-readable (JSON) and human-readable formats where applicable
- Return codes MUST be meaningful (0 = success, non-zero = specific error types)

**Documentation Requirements**:
- Every feature MUST have user-facing documentation before release
- Documentation MUST include practical examples and common workflows
- Breaking changes MUST be clearly documented with migration guides
- Error messages MUST reference relevant documentation where applicable

**User Journey Validation**:
- Every feature specification MUST include prioritized user stories (P1, P2, P3)
- Each user story MUST be independently testable and deliverable
- MVP MUST focus on P1 user stories only
- User experience testing MUST validate acceptance scenarios from spec

**Consistency Checklist**:
- [ ] Input/output formats consistent with existing features
- [ ] Error messages actionable and consistent in tone
- [ ] Documentation includes examples and edge cases
- [ ] User stories independently testable
- [ ] Breaking changes documented with migration path

**Rationale**: Consistent interfaces reduce cognitive load, make features discoverable, and improve user satisfaction. Independent user stories enable iterative delivery and clear value demonstration.

### V. Use Lots of Emojis

Use emojis in output.
Be happy!

## Code Quality Standards

### Static Analysis
- Linting MUST be configured for project language and framework
- Formatting MUST be automated (Prettier, Black, rustfmt, etc.)
- Type checking MUST be enabled in strict mode where available
- Pre-commit hooks MUST enforce linting and formatting

### Security Standards
- Secrets MUST NOT be committed to repository (use environment variables or secure vaults)
- Dependencies MUST be scanned for known vulnerabilities
- Security-sensitive operations MUST be logged
- Input validation MUST be performed at system boundaries

### Performance Standards
- Performance-critical paths MUST be profiled and benchmarked
- Database queries MUST be optimized (use indexes, avoid N+1 queries)
- Large datasets MUST be paginated or streamed (no loading entire datasets in memory)
- Caching MUST be used judiciously (cache invalidation strategy required)

## Development Workflow

### Feature Development Process
1. **Specification Phase** (`/speckit.specify`):
   - Define user stories with priorities (P1, P2, P3)
   - Document acceptance criteria
   - Validate specification completeness
   
2. **Planning Phase** (`/speckit.plan`):
   - Constitution check MUST pass or violations MUST be justified
   - Technical context MUST be documented
   - Project structure MUST be defined
   
3. **Task Generation** (`/speckit.tasks`):
   - Tasks organized by user story priority
   - Each user story MUST be independently implementable
   - Tests written first (if required in spec)
   
4. **Implementation Phase** (`/speckit.implement`):
   - Implement in priority order (P1 → P2 → P3)
   - Each user story validated independently before next
   - Quality gates enforced at each checkpoint

### Branch Strategy
- Feature branches named: `###-feature-name`
- Branch per feature specification
- Merge only after all quality gates pass

### Code Review Requirements
- At least one approval required before merge
- Reviewer MUST verify constitution compliance
- Reviewer MUST verify test coverage and quality
- Reviewer MUST verify documentation completeness
- Reviewer MUST verify user documentation is created and up-to-date before merge to master

### Documentation Merge Requirements (NON-NEGOTIABLE)
**User documentation MUST be complete and current before any merge to master branch.**

- User-facing documentation MUST be created for all new features
- Existing documentation MUST be updated when feature behavior changes
- Documentation MUST include:
  - Clear description of feature purpose and usage
  - Practical examples demonstrating common use cases
  - Edge cases and error handling guidance
  - Breaking changes and migration instructions (if applicable)
- Documentation changes MUST be reviewed as part of code review process
- Missing or outdated documentation BLOCKS merge to master (exceptions require explicit justification)

**Rationale**: Out-of-date documentation creates user frustration, increases support burden, and undermines trust in the product. Enforcing documentation completeness at merge time ensures users always have accurate information.

### Complexity Justification
- Any violation of constitution principles MUST be justified in plan.md complexity tracking table
- Justification MUST explain why simpler alternatives are insufficient
- Complexity MUST be approved during code review

## Governance

### Constitutional Authority
This constitution supersedes all other development practices, style guides, and conventions. When conflicts arise, constitution principles take precedence.

### Amendment Process
1. Amendments MUST be proposed with clear rationale
2. Amendments MUST be reviewed by team leads
3. MAJOR version bump: Backward-incompatible changes (e.g., removing principles, changing non-negotiable requirements)
4. MINOR version bump: New principles, expanded guidance, new sections
5. PATCH version bump: Clarifications, typo fixes, wording improvements
6. Amendments MUST include migration plan for affected projects
7. All dependent templates MUST be updated to reflect amendments

### Compliance Review
- Constitution compliance MUST be checked during planning phase
- Violations MUST be documented in complexity tracking table
- Repeated violations without justification trigger architecture review
- Constitution review occurs quarterly to validate continued relevance

### Template Synchronization
- Changes to constitution MUST trigger review of:
  - `.specify/templates/spec-template.md`
  - `.specify/templates/plan-template.md`
  - `.specify/templates/tasks-template.md`
  - `.specify/templates/commands/*.md`
- Template updates MUST be completed before constitution amendment is finalized
- Version alignment MUST be maintained across all governance documents

### Decision Framework
When making technical decisions, consider in order:
1. **Does this violate constitutional principles?** → If yes, justify or choose alternative
2. **Does this increase complexity?** → If yes, can it be simpler?
3. **Is this testable?** → If no, redesign for testability
4. **Is this consistent with existing patterns?** → If no, justify divergence
5. **Will users understand this?** → If no, improve clarity or documentation

**Version**: 1.1.0 | **Ratified**: 2025-11-17 | **Last Amended**: 2025-11-17
