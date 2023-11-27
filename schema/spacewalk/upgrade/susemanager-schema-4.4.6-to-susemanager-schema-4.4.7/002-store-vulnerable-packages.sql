CREATE OR REPLACE PROCEDURE
    insert_product_vulnerable_packages(package_name_in varchar,fix_version_in varchar,product_cpe_in varchar,cve_name_in varchar)
AS
$$
DECLARE
    cve_id_val numeric;
    product_cpe_id_val numeric;
    vulnerable_pkg_id_val numeric;
begin

    IF NOT exists(SELECT cve FROM rhnCve cve WHERE cve.name = cve_name_in) THEN
        INSERT INTO rhncve(id, name)
        VALUES (nextval('rhn_cve_id_seq'), cve_name_in);
    END IF;

    SELECT id INTO cve_id_val FROM rhncve WHERE name = cve_name_in;

    IF NOT exists(SELECT c FROM suseOVALPlatform c WHERE cpe = product_cpe_in) THEN
        INSERT INTO suseovalplatform(id, cpe)
        VALUES (nextval('suse_oval_platform_id_seq'), product_cpe_in);
    END IF;

    SELECT id INTO product_cpe_id_val FROM suseOVALPlatform WHERE cpe = product_cpe_in;

    IF NOT EXISTS(SELECT 1
                  FROM suseovalvulnerablepackage
                  WHERE name = package_name_in
                    AND ((fix_version IS NOT NULL AND fix_version = fix_version_in) OR
                         (fix_version IS NULL AND fix_version_in IS NULL))) THEN
        INSERT INTO suseovalvulnerablepackage(id, name, fix_version)
        VALUES (nextval('suse_oval_vulnerable_pkg_id_seq'), package_name_in, fix_version_in);
    END IF;

    SELECT id
    INTO vulnerable_pkg_id_val
    FROM suseovalvulnerablepackage
    WHERE name = package_name_in
      AND ((fix_version IS NOT NULL AND fix_version = fix_version_in) OR
           (fix_version IS NULL AND fix_version_in IS NULL));

    INSERT INTO suseOVALPlatformVulnerablePackage(platform_id, cve_id, vulnerable_pkg_id)
    VALUES (product_cpe_id_val, cve_id_val, vulnerable_pkg_id_val)
    ON CONFLICT(platform_id, cve_id, vulnerable_pkg_id) DO UPDATE
        SET platform_id       = EXCLUDED.platform_id,
            cve_id            = EXCLUDED.cve_id,
            vulnerable_pkg_id = EXCLUDED.vulnerable_pkg_id;
end;
$$ language plpgsql;