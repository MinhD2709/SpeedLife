# Frontend checks

Run `npm run build` in `frontend/` for strict TypeScript and production bundling.
Manual smoke test with the API running:

1. Open localhost:5173; select a text PDF and submit.
2. Confirm excerpt text, filename, page number, source evidence, and demo label.
3. Print or save to PDF; the upload form should be hidden.
4. Try invalid and oversized files, empty selection, and an unavailable API.
5. Check keyboard access, narrow screens, and the announced busy/error states.

No browser automation framework has been added yet.
