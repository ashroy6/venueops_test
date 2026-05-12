# Production Approval

## GitHub Environment

Production deployments should use a GitHub Environment named:

    production

Recommended settings:

- required reviewers enabled
- only senior engineers can approve
- deployment branch restricted to main
- secrets scoped to the production environment
- deployment history retained

## Production Deployment Flow

1. Code is merged to main after checks pass.
2. Deploy Prod workflow is triggered manually.
3. GitHub requests approval from production reviewers.
4. After approval, the workflow deploys to AKS using Helm.
5. Rollout status is checked.
6. Post-deploy smoke test runs.
7. Evidence is stored as workflow artifacts.

## Why This Matters

Production deployment should be intentional.

Manual approval prevents accidental deployment from normal code pushes.
