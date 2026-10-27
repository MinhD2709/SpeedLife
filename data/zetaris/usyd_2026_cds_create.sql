-- Run each complete statement separately, following the Zetaris getting-started
-- runner instructions. Replace CATALOG_URL with the raw, public URL of
-- backend/app/data/usyd_2026_cds.json at a fixed commit or release tag.

CREATE LIGHTNING DATABASE UNIPILOT_REST DESCRIBE BY "Versioned public USYD handbook catalogue for UniPilot";

CREATE SCHEMASTORE CONTAINER unipilot;

CREATE LIGHTNING REST TABLE usyd_2026_cds_catalog FROM UNIPILOT_REST REQUEST(
    endpoint "CATALOG_URL",
    method "get",
    response_type "json",
    http_encoding "URLENCODED"
) HEADER (
) BODY ();

CREATE SCHEMASTORE VIEW usyd_2026_cds_units WITH CONTAINER unipilot AS
SELECT
    unit.code,
    unit.title,
    unit.credit_points,
    unit.level,
    unit.requirement_group,
    unit.core,
    unit.sessions,
    unit.prerequisites,
    unit.corequisites,
    unit.prohibitions,
    unit.assumed_knowledge,
    unit.source_url,
    unit.handbook_year
FROM unipilot_rest.usyd_2026_cds_catalog
LATERAL VIEW explode(units) AS unit;

-- Verification
SELECT code, title, requirement_group
FROM unipilot.usyd_2026_cds_units
ORDER BY code;
