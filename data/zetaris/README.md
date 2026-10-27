# Zetaris Codespace setup

1. Create the confirmed 4-core/16 GB x86 Codespace and install Docker.
2. Download `zetaris-platform.zip` and the registry sign-in command from Zetaris Cloud.
3. Follow the platform bundle's setup, run `./preflight.sh`, then `docker compose pull`,
   `docker compose up -d`, and `./verify.sh`.
4. Publish `backend/app/data/usyd_2026_cds.json` from a fixed public commit or release.
   It contains public handbook facts only. Never publish uploaded student records.
5. Replace `CATALOG_URL` in `usyd_2026_cds_create.sql`. Dry-run and then execute one
   statement at a time with Zetaris's official `scripts/run_sql.py` helper.
6. Create a Zetaris API key in the UI and keep it private.
7. On the Mac, keep both ports private and run:

   ```sh
   gh codespace ports forward 3000:3000 8888:8888 -c YOUR_CODESPACE
   ```

8. Put the forwarded REST URL, organization ID and key in the root `.env`, switch
   `APP_MODE=live`, and check `GET /api/integrations/status`.

The SQL follows the official Lightning REST table + SchemaStore view pattern. The
catalogue is intentionally versioned to handbook year 2026; update it deliberately
rather than silently mixing curriculum years.
