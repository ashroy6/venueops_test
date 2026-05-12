# Branch Protection

## Recommended GitHub Branch Rules

The `main` branch should be protected.

Recommended rules:

- require pull request before merge
- require approvals
- require conversation resolution before merge
- require status checks before merge
- require branches to be up to date before merge
- block force pushes
- block branch deletion
- restrict who can push to main

## Required Status Checks

Recommended required checks:

- CI
- Security Scan
- Terraform Validate
- Helm Validate
- KEDA and AKS Hardening
- Image Scan and SBOM

## Branch Model

Development work should happen on:

    dev

Stable production-ready code should live on:

    main

Flow:

    feature branch -> dev -> pull request -> main

## Why This Matters

Production systems should not allow direct unreviewed changes to the stable branch.

Branch protection gives an audit trail and prevents accidental or unsafe changes.
