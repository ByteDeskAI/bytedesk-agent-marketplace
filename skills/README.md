# Skills

Optional portable skill packages referenced by manifests in `agents/`. Skill
contents (scripts, binaries, archives, data, dependency manifests) are
untrusted, declared data: nothing here is ever executed by this repository's
validation, build, or CI. A consumer runtime may execute a skill only after
explicitly approving its exact digest under its own sandbox and
authorization controls.

Empty today: no skill package format or validator is implemented yet, and an
empty `skills/` never blocks agent validation or import
(`tests/test_validate_agents.py::test_empty_skills_directory_does_not_block_validation`).
Add skill-package scanning to `scripts/validate_agents.py` when the first
skill package lands.
