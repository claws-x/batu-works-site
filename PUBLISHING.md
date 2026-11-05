# BATU WORKS website publishing

The public website repository holds public-facing material. Website changes are prepared on a review branch with a preview and validation results.

## Release approval

Ben explicitly approves the reviewed revision before it is merged or deployed. The technical review verifies the content and tests. Release approval is a separate decision. Confirm the configured GitHub Pages source before a release, and record the deployed revision and public URL after verification.

## Legacy announcement workflow

The existing issue-based workflow accepts an owner-authored request and an `approved` field. A caller able to post as the owner can supply both, so this is not independent release authorization. Keep announcement changes in the reviewed PR process until there is a separate, verifiable approval mechanism. Treat public issue bodies as public material.

## Verification and rollback

Run `python3 scripts/check_site.py` before requesting approval. After deployment, open the public homepage and changed pages, verify their content and navigation, and record the Pages deployment revision. If rollback is needed, revert the release changes in a new reviewed PR and verify the public pages after redeployment.
