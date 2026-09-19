# Repository-versus-live evidence in reviews

Use this matrix when reviewing identity-specific automation, cron jobs, skills, plugins, or host-local integrations.

| Observed evidence                                               | Supported conclusion                                                         | Unsupported conclusion                                      |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Dependency absent from tracked files and setup installer        | The repository does not provision it through the inspected path              | It is absent from the target host                           |
| Dependency absent from a different assistant or reviewer host   | That reviewer host lacks it                                                  | The named deployment host lacks it                          |
| Cron/job JSON contains an attached skill name                   | Registration persisted the requested identifier                              | The skill resolves and loads successfully at execution time |
| Installer accepts an arbitrary dependency identifier            | Installation/registration can complete without validating runtime resolution | The dependency is available                                 |
| Authorized target-host lookup resolves and loads the dependency | It is available at the observed host state and time                          | It is reproducibly installed on every rebuild               |
| Governed setup installs and verifies the dependency             | Rebuild provisioning is covered by that setup path                           | Every live host has already applied the setup               |

## Review sequence

1. Identify the contract: portable repository product, identity-specific product, or deliberately host-local integration.
2. Separate four questions: does the repo declare it, does setup provision it, does the target host currently have it, and does the runtime actually resolve it?
3. Inspect the original source for each claim. Do not substitute another host's state for the named target.
4. If live access is unavailable, report the repository observation and the unresolved live question separately.
5. Grade severity from the actual contract. An undeclared host-local dependency is not automatically a blocker for an identity-owned job.
6. If a review overstated a claim, publish a superseding exact-head correction. Explicitly withdraw only the unsupported finding and retain independent stale-base, CI, draft, authorization, or deployment gates.

## Proportionate guidance-review checklist

Use this for cron prompts, standing orders, identity instructions, and similar prose embedded in executable files:

1. Identify whether the changed lines are guidance, registration metadata, executable control flow, or a mixture.
2. Read the final rendered guidance for contradictions, impossible deadlines, ambiguous authority, duplicate delivery, unsafe escalation, and missing finalization/cleanup ownership.
3. Validate the enclosing file format or syntax. This proves the container remains valid; do not describe it as behavioral coverage of the prose.
4. Check any functional metadata separately, such as an attached skill name or delivery target. Verify only what the available source supports.
5. Request a durable regression only when a stable machine-checkable invariant exists and the repository already treats that class as governed behavior, or when a recurring failure justifies the maintenance cost.
6. Otherwise record tests as optional hardening, not a merge blocker. Identity-owner semantic rereview is often stronger evidence than brittle substring assertions.
7. Keep content verdict and integration readiness separate. A good text change can be approved while its draft/base/CI/deployment sequence remains pending.

## Wording patterns

Prefer:

- “This dependency is not provisioned by the inspected repository setup; I have not verified whether it is installed on the target host.”
- “The job records the skill identifier, but registration alone does not prove runtime resolution.”
- “Content is approved; integration remains blocked on a newer base and fresh CI.”

Avoid:

- “The skill is not installed” when only repository search was performed.
- “The host is misconfigured” based on another assistant's environment.
- Turning a portability suggestion into a blocker without first establishing portability as a requirement.
