# Git Workflow

## Branching

- Always create a new branch for any work. Never commit directly to `main`.
- Branch naming: `<type>/<short-description>` using kebab-case.
  - `feat/add-user-auth`
  - `fix/login-redirect-loop`
  - `chore/update-dependencies`
  - `docs/api-reference`
  - `refactor/simplify-parser`
- Branch off `main` unless otherwise specified.

## Commits

- Use conventional commit messages: `<type>: <description>`
  - `feat:` — new feature
  - `fix:` — bug fix
  - `chore:` — maintenance, dependencies, config
  - `docs:` — documentation only
  - `refactor:` — code change that neither fixes a bug nor adds a feature
  - `test:` — adding or updating tests
  - `style:` — formatting, whitespace, no code change
- Keep commits atomic — one logical change per commit.
- Write concise descriptions in imperative mood (e.g., `feat: add login endpoint`, not `feat: added login endpoint`).

## Pushing

- Use `git push -u origin <branch>` on first push to set upstream tracking.
- Never force-push to `main`.

## Pull Requests

- All changes reach `main` via pull request. Never merge or push to `main` directly without explicit permission.
- PR title should match conventional commit style (e.g., `feat: add user authentication`).
- PR body should include a summary of changes and a test plan.
- Target `main` as the base branch unless told otherwise.
- Always use squash and merge when merging PRs, never merge commits.
- Delete the branch (both local and remote) after merging.

## General

- Run `git status` and `git diff` before committing to review changes.
- Stage files explicitly by name — avoid `git add .` or `git add -A`.
- Do not pull, merge, or rebase into `main` without explicit permission.
