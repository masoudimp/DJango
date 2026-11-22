# Django Take-Home Assignment — Agent Instructions

## Purpose and scope

Build the Django take-home assignment for Remarcable, Inc. This document turns the supplied assignment into actionable requirements for an implementation agent. Creating this document does not mean the implementation is complete.

Focus on functional Django models, relationships, querysets, views, and clear documentation. Styling and visual design are not evaluation priorities. Keep the implementation small enough for an assignment intended to take a few hours.

## Conflicts with the original assignment

Before implementing a user decision, check whether it conflicts with the original Remarcable assignment supplied by the user, including its deliverables, submission requirements, and AI policy.

- If there is a conflict, **warn the user before taking the conflicting action**. Identify the original requirement, explain how the requested decision differs, and describe the concrete impact on assignment compliance or evaluation.
- Suggest a compliant alternative when useful, then continue with the user's requested direction after giving the warning. This warning rule does not itself require another confirmation or a pause.
- Record the decision, the conflicting requirement, and the warning in [the decision log](decisions.md). Keep any affected README notes accurate, and do not mark an unmet requirement as complete or claim the result fully complies with the assignment.
- Distinguish actual employer requirements from this document's recommendations and agent assumptions. A different permitted approach is not a conflict; for example, the employer explicitly allows either Django templates or a front-end framework.
- If the original requirement is ambiguous, explain the uncertainty instead of presenting an inferred restriction as a requirement.

## 1. Inspect and plan

- [ ] Read repository instructions and existing source before making changes.
- [ ] Read [the decision log](decisions.md) before implementation and record meaningful decisions, alternatives, rationale, and tradeoffs there as work progresses. Keep its entries and the README consistent with the implementation.
- [ ] Identify what already exists and preserve unrelated user changes.
- [ ] Choose a simple Django project structure and record necessary assumptions in the README.
- [ ] Prefer Django templates unless there is a concrete reason to introduce a separate front end.

## 2. Models and database

- [ ] Create `Product`, `Category`, and `Tag` models.
- [ ] Include a product description that can be searched.
- [ ] Define appropriate relationships between products, categories, and tags.
- [ ] Include and commit database migrations.
- [ ] Give models readable string representations for the admin and HTML interface.

The assignment does not specify exact fields, category cardinality, or tag matching semantics. A reasonable default is one category per product using a foreign key, and multiple tags per product using a many-to-many relationship. Document the chosen relationships and deletion behavior rather than presenting these choices as explicit requirements from the employer.

## 3. Admin and sample data

- [ ] Register all three models with Django admin.
- [ ] Make it possible to enter products and assign categories and tags through the admin.
- [ ] Document migration and superuser creation commands.
- [ ] Use the Django admin interface to populate at least **5 categories**, **10 tags**, and **20 products**.
- [ ] Include varied descriptions, categories, and tag combinations so combined filters can be demonstrated.
- [ ] Verify the final counts and document how a reviewer can reproduce the sample dataset.

Fixtures or seed commands may be optional conveniences, but do not substitute them for the explicitly required admin-based data entry. Do not claim admin population occurred unless it was actually performed. If that step requires the user's participation, provide concrete entry instructions and clearly report it as outstanding. Do not commit passwords, credentials, or an admin account's password hash as sample data.

## 4. Search, filters, and querysets

- [ ] Build a product listing view and URL.
- [ ] Support searching products by description.
- [ ] Support filtering products by category.
- [ ] Support filtering products by tags, including selection of multiple tags.
- [ ] Allow description, category, and tag filters to be combined in the same request.
- [ ] Construct filtering with Django querysets.
- [ ] Avoid duplicate products when filtering across many-to-many relationships.
- [ ] Handle empty search terms, no filters, no matches, and invalid filter values predictably.
- [ ] Document whether multiple selected tags mean “any selected tag” or “all selected tags.” The assignment does not mandate either interpretation.
- [ ] Keep database access efficient when displaying category and tag information.

Recommended implementation choices: GET parameters for bookmarkable searches, case-insensitive description matching, and appropriate related-object loading. These are engineering recommendations, not additional employer requirements.

## 5. HTML interface

- [ ] Provide a description search input.
- [ ] Provide a category selector.
- [ ] Provide controls for selecting tags.
- [ ] Provide a way to submit combined search and filter selections.
- [ ] Preserve active selections after submission.
- [ ] Display matching products and enough information to confirm filtering works.
- [ ] Display a clear empty-results message.
- [ ] Keep styling simple; do not let visual polish displace required functionality.

## 6. Verification

- [ ] Run Django's system checks and apply migrations successfully.
- [ ] Verify description search, category filtering, and tag filtering individually.
- [ ] Verify combined description/category/tag filtering.
- [ ] Verify multiple-tag semantics and that each matching product appears only once.
- [ ] Verify unfiltered results, no matches, and malformed or unknown filter values.
- [ ] Add focused automated tests for meaningful query and view behavior.
- [ ] Verify the admin supports data entry and the required sample-data counts are met.
- [ ] Check that a fresh setup can follow the README successfully.
- [ ] Report the checks actually run, their results, and any unresolved issues.

## 7. README and deliverables

- [ ] Deliver a complete Django project with all source code and migrations.
- [ ] List prerequisites and supported Python/Django versions.
- [ ] Provide dependency installation and virtual environment instructions.
- [ ] Explain configuration and any required environment variables without exposing secrets.
- [ ] Provide commands to migrate, create a superuser, and start the application.
- [ ] Identify the product listing and admin URLs.
- [ ] Explain how to populate the required sample data through the admin.
- [ ] Explain how to run tests.
- [ ] Document model relationships, filter semantics, assumptions, and additional notes.
- [ ] Include front-end build instructions if using a separate front-end framework.
- [ ] Include accurate AI attribution as described below.

## 8. AI policy — mandatory

The employer permits AI assistance but is evaluating the applicant's own technical skills. The agent must support the applicant's understanding and must not claim AI-generated work is solely the applicant's work.

- [ ] **Understanding and ownership:** Explain generated code and key design decisions so the applicant can understand every part of the submission. The applicant must be able to explain the implementation during the interview; inability to do so can result in disqualification.
- [ ] **Enhancement and originality:** The employer requires AI-generated code to be modified and expanded with significant personal contributions. Raw AI-generated code is not an acceptable submission and can result in immediate disqualification. Further agent-generated changes do not establish the applicant's personal contributions.
- [ ] **Attribution:** Clearly document in the README how and where AI was used to generate code. Inline comments or docstrings may supplement the disclosure. Keep attribution accurate as work evolves.
- [ ] Do not fabricate personal contributions, understanding, manual data entry, testing, or completion claims.
- [ ] Before describing the project as submission-ready, identify any remaining applicant review, understanding, and personal contribution steps. These cannot be certified by an agent on the applicant's behalf.

By submitting, the applicant acknowledges the employer's AI policy.

## 9. Submission and deadline

- [ ] Ensure the final project is available in a **public** Git repository; private repositories are not accepted.
- [ ] Ensure all required source files, migrations, dependency declarations, tests, and documentation are committed and pushed as part of the authorized submission work.
- [ ] Verify that the published repository contains the intended final work.
- [ ] Provide the repository link for review.
- [ ] Complete submission within **5 days / 120 hours of the original assignment request's date and time**. The supplied text does not include that timestamp; do not invent a deadline or use the date this document was created as its substitute.
- [ ] If the submission portal requires files or notes, prepare the required material and report any remaining submission action accurately.

The employer may schedule a virtual interview after successful completion and review. This is an expected next step, not an implementation task. The supplied text allows questions or clarification to the employer; do not send messages on the applicant's behalf without authorization.

## 10. Evaluation and completion report

Check the final implementation against each evaluation criterion:

| Criterion | What to demonstrate |
| --- | --- |
| Functionality | Correct models, relationships, search, and combined filters |
| Code quality | Clean, readable, organized code |
| Documentation | Clear setup instructions and useful code comments |
| Query proficiency | Correct and effective Django querysets |
| Completion | All required functionality, data, documentation, and deliverables |

When finishing work, explain what changed, why the approach was chosen, what was verified, and what remains for the applicant. Mark checklist items complete only when supported by actual work or verification. Distinguish local implementation, repository publication, and portal submission.

## Source context

Based on the assignment text supplied by the user for [Remarcable, Inc.](https://www.remarcable.com/). Branding images, upload widget labels, and Ashby footer links are portal presentation elements, not requirements for the Django application.
