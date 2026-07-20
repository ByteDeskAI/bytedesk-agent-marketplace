# Skills

Optional portable skill packages referenced by manifests in `agents/`. Skill
contents (scripts, binaries, archives, data, dependency manifests) are
untrusted, declared data: nothing here is ever executed by this repository's
validation, build, or CI. A consumer runtime may execute a skill only after
explicitly approving its exact digest under its own sandbox and
authorization controls.

Empty until the first skill package lands.
