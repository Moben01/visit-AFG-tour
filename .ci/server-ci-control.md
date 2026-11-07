# Server governance adoption

This additive baseline runs on GitHub-hosted infrastructure. It parses Python
source without importing application settings, reading environment files or
connecting to any database. Existing application and deployment workflows remain
in place. A successful baseline is not application QA or deployment authorization.

The profile records the unfinished adoption gates explicitly. No staging or
production adapter is enabled by this change. Do not use the capacity readiness
probe as a substitute for holding a reservation throughout the actual environment
lifetime. Root-owned host policy remains authoritative.

Before enabling a project adapter:

1. Preserve and reconcile live-source changes against an exact reviewed commit.
2. Run application tests with synthetic data and isolated credentials. Tenant and
   migration assurance requires the application's established PostgreSQL gates.
3. Use distinct databases, database users, secrets, uploaded-file storage and
   hostnames for production and testing. Never mount production data into previews.
4. Build outside the production host. Reserve host-wide RAM, disk and inode
   capacity before extraction or launch, enforce process/container limits, record
   owned resources, retain the reservation until teardown is verified, and attach
   an expiry/owner to each preview. Cancellation must not orphan resources.
5. Configure an offsite backup destination, encryption and a tested restore. The
   owner currently has no separate backup destination; this is an open gate.
6. Preserve existing exact-commit production approvals, take a verified backup,
   use a bounded health check and record rollback evidence before promotion.

Never delete a legacy release merely because it is old. Existing Chopan and
Hesabdar staging work is protected until ownership is verified. Never run volume
pruning, unscoped recursive deletion, or automatic database restoration.

The shared private framework is `Moben01/server-ci-control`. Public repositories
use this self-contained baseline to avoid requiring access tokens for that repo.
Updates are generated from a pinned framework revision and reviewed as code.
