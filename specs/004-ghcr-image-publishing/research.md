# Research: GHCR Image Publishing

## Decisions

### Workflow permissions and token

- **Decision**: Give the workflow a default `contents: read` permission. The pull request validation job receives only that permission. The main-branch publisher job adds `packages: write` and authenticates with the built-in `GITHUB_TOKEN`.
- **Rationale**: GitHub's package publishing guidance uses `contents: read` and `packages: write`; job-level separation keeps package-write permission out of pull request runs. No long-lived credential is needed.
- **Alternatives considered**: A shared job with `packages: write` and a conditional push was rejected because pull request runs would still receive the write permission. A personal access token was rejected because the built-in token is sufficient.
- **Sources**: [GitHub Actions package publishing](https://docs.github.com/en/packages/managing-github-packages-using-github-actions-workflows/publishing-and-installing-a-package-with-github-actions); [GITHUB_TOKEN permissions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication).

### Triggers and job separation

- **Decision**: Trigger on `pull_request` targeting `main` and on `push` to `main`. Run a build-only job for the pull request event and a separate publishing job only for a main push.
- **Rationale**: The clarified spec limits image checks to PRs targeting `main`. Keeping separate jobs makes the permission boundary explicit, including for fork pull requests. Both jobs build the same Dockerfile.
- **Alternatives considered**: `pull_request_target` and `workflow_run` were rejected because they are unnecessary and introduce privileged-trigger risks. A single job with conditional push was rejected because package-write access would be present in PR execution.
- **Sources**: [GitHub Docker image publishing guidance](https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images); [GitHub Actions secure use reference](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions).

### Image tags and repository association

- **Decision**: Publish `ghcr.io/mtak/opsgenie-google-calendar-sync:<full commit SHA>` and `:latest` from the main publisher. Use Docker metadata tag strategies `type=sha,format=long,prefix=` and `type=raw,value=latest`, only in the main publisher job. Pass generated metadata labels to the image build so the OCI source label associates the package with this repository.
- **Rationale**: The metadata action supports a full-length source SHA, lowers image names to registry-valid form, and generates the `org.opencontainers.image.source` label. GHCR recommends linking the package to the repository before publication so the workflow token can access it. `latest` remains a convenience reference; deployment config is outside scope and must use the selected SHA tag.
- **Alternatives considered**: The metadata action's default short SHA is insufficient; the full format is required. Omitting the OCI source label risks creating an unlinked package that the repository workflow cannot subsequently write to.
- **Sources**: [docker/metadata-action tag strategies and labels](https://github.com/docker/metadata-action); [GitHub Container registry guidance](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry).

### Public visibility setup

- **Decision**: Document that the first GHCR package is private by default and a maintainer must open the package's settings and change visibility to Public. If an existing package is not linked to the repository or does not grant the repository Actions access, the maintainer must connect the repository and grant workflow access before publishing.
- **Rationale**: A public GHCR container package permits anonymous pulls. Package linking/access and visibility are distinct settings; one does not imply the other.
- **Alternatives considered**: Making visibility an automated workflow concern was rejected because visibility is a package admin setting and requires maintainer authority.
- **Sources**: [Container registry visibility and linking](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry); [package access and visibility](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility).

### Third-party action pins

- **Decision**: Pin all third-party actions to full commit SHAs and retain a human-readable release comment. Candidate pins for implementation are:

  | Action | Release | Full commit SHA |
  |---|---|---|
  | `actions/checkout` | `v7.0.1` | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
  | `docker/setup-buildx-action` | `v4.4.1` | `f87e5991a6d7451dcb8d9637bfbc97413f497069` |
  | `docker/login-action` | `v4.6.0` | `dbcb813823bdd20940b903addbd779551569679f` |
  | `docker/metadata-action` | `v6.2.0` | `dc802804100637a589fabce1cb79ff13a1411302` |
  | `docker/build-push-action` | `v7.4.0` | `c3c9e263c25d99ce0380d002d59b67737d91b0dc` |

- **Rationale**: Full commit references prevent a mutable version tag from changing the executed action. The Docker action pins were checked against the corresponding official GitHub repository release refs; checkout reuses the exact pin already present in the repository's quality workflow. Reconfirm the selected release refs when implementing if the work is delayed.
- **Alternatives considered**: Mutable major-version tags (for example, `@v7`) were rejected because repository conventions and the specification require full SHA pins.
- **Sources**: [GitHub pinning guidance](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions#using-third-party-actions); [official Docker action release repositories](https://github.com/docker/setup-buildx-action/releases), [login](https://github.com/docker/login-action/releases), [metadata](https://github.com/docker/metadata-action/releases), [build-push](https://github.com/docker/build-push-action/releases). The action commit refs were also resolved with `git ls-remote` against each official repository.

## Resolved Unknowns

- GHCR registry and token are specified by the feature requirements.
- The image path is the lower-case owner/repository path `ghcr.io/mtak/opsgenie-google-calendar-sync`.
- The Dockerfile is a single-platform Python 3.12 image; no QEMU, matrix, or multi-platform setup is required.
- Validation is local `docker build` plus GitHub Actions workflow lint/static policy review; package publication is verified through the main workflow after merge.
