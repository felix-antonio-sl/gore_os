# dmux Hooks

This directory contains optional, versioned examples for dmux lifecycle hooks.
No hook is active while it keeps the `.example` suffix.

## Quick Start

1. Read [`README.md`](../README.md) to run the system and
   [`AGENTS.md`](../AGENTS.md) before changing it.

2. Choose one file from `examples/`.

3. Copy it without the `.example` suffix and make it executable:

   ```bash
   cp .dmux-hooks/examples/run_test.example .dmux-hooks/run_test
   chmod +x .dmux-hooks/run_test
   ```

4. Run the hook directly before relying on a dmux lifecycle event:

   ```bash
   export DMUX_ROOT="$(pwd)"
   export DMUX_WORKTREE_PATH="$(pwd)"
   ./.dmux-hooks/run_test
   ```

## Examples

- `worktree_created.example`
- `post_merge.example`
- `run_test.example`
- `run_dev.example`

Active hooks are repository-local behavior. Keep only hooks that protect a current,
observable workflow.
