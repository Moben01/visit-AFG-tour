# Larmoond Travel and Tours

This Django repository powers the public website, trip planning, quotations,
bookings, traveller coordination and tour operations for Larmoond Travel and
Tours.

The relaunch architecture, audit, migration risks and verification commands are
documented in [`docs/relaunch/`](docs/relaunch/). Development and deployment
work must follow [`AGENTS.md`](AGENTS.md), including its data-protection rules
and prohibition on direct production deployment.

Run the isolated test suite with:

```powershell
python -B manage.py test --settings=visit_afg_core.test_settings
```
