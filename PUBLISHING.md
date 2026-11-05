# BATU WORKS website publishing

The public website repository holds public-facing material. Website changes are prepared on a review branch with a preview and validation results.

## Release approval

Ben explicitly approves the reviewed revision before it is merged or deployed. The technical review verifies the content and tests. Release approval is a separate decision. Confirm the configured GitHub Pages source before a release, and record the deployed revision and public URL after verification.

## Announcement changes

Update `updates.json` through a reviewed PR. The Issue-triggered publisher and its deployment hook were removed. Public issues and approval fields in issue text cannot authorize an announcement. GitHub Pages deploys the approved `main` revision after a qualifying push, or on an authorized manual redeployment.

## Verification and rollback

Run `python3 scripts/check_site.py` before requesting approval. After deployment, open the public homepage and changed pages, verify their content and navigation, and record the Pages deployment revision. If rollback is needed, revert the release changes in a new reviewed PR and verify the public pages after redeployment.
