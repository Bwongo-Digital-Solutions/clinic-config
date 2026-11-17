# Bahmni Clinic configuration and data.

### [![Bahmni Config](https://github.com/Bahmni/clinic-config/actions/workflows/build_upload.yml/badge.svg)](https://github.com/Bahmni/clinic-config/actions/workflows/build_upload.yml)

This repo represents configuration for BahmniLite (more applicable for clinics).

## Deploy the published ClinicHIS configuration image

The Bahmni Lite deployment consumes the published configuration image from GitHub Container Registry (GHCR). Once the GitHub Actions image-build workflow has completed successfully for the updated `dev` branch, update the running deployment from the Bahmni Lite directory:

```bash
cd /home/eron/CLINICEMR/bahmni-docker/bahmni-lite

# Pull the image/tag configured for the bahmni-config service.
docker compose pull bahmni-config

# Recreate the config seeder and services that consume the shared config volume.
docker compose up -d --force-recreate bahmni-config openmrs bahmni-web

# Confirm service state and inspect startup/import logs.
docker compose ps
docker compose logs --tail=200 bahmni-config openmrs
```

You can also pull the image explicitly with `docker pull ghcr.io/bwongo-digital-solutions/uganda-clinic-config:dev`, but `docker compose pull bahmni-config` is preferred because it uses the image and tag configured by the deployment's Compose file. Pulling an image alone does not update an already-running container; recreate the config seeder and its consumers as shown above.

**Do not run `docker compose down -v` for a configuration update.** The named volumes contain application and database state and must be preserved.

## Uganda address hierarchy and import behavior

The Uganda hierarchy is packaged in the configuration image. Its import configuration uses `<wipe>true</wipe>` so that, when the Address Hierarchy importer processes this configuration, it replaces the existing hierarchy entries (including the old India hierarchy) before importing Uganda's hierarchy.

The wipe is limited to the Address Hierarchy lookup tables. It does not delete patient records, patient addresses, visits, encounters, or other OpenMRS clinical data. Patient address values are stored as text.

A previous manual import does not, by itself, disable a later wipe. However, OpenMRS Initializer may skip a configuration file it has already processed when its checksum has not changed. In that case, the importer does not execute again and the wipe is not repeated. If the hierarchy configuration is processed again, `<wipe>true</wipe>` is applied again.

For dataset source, attribution, format, and refresh instructions, see [the Uganda address hierarchy notes](masterdata/configuration/addresshierarchy/README.md).

## References to openmrs-module-initializer for Bahmni

https://github.com/CRUDEM/openmrs-config-hsc

https://github.com/Siko099/openmrs-config-uganda

## Steps to follow for openmrs initializer to load masterdata [For Development Purpose]

Step 1: Latest OpenMRS image is already packaged with openmrs-initializer-module. Make sure you have **openmrs-initializer-module** in modules directory (`/openmrs/data/modules`). If not, **copy or package openmrs-initializer-module** into your OpenMRS modules.

Step 2: Follow the steps [here](https://github.com/Bahmni/bahmni-package/tree/master/bahmni-docker#local-development-on-config) to volume mount your local folder.

Step 3: Make sure we have CSV files with respective folder names inside **masterdata/configuration** folder in the **source folder** of **clinic-config**:

```text
configuration/
├── addresshierarchy/
├── locations/
├── privileges/
└── roles/
```

Step 4: Starting Docker Compose would load OpenMRS Initializer.

Step 5: During local development, after changing files in the `masterdata` folder, restart OpenMRS with `docker compose restart openmrs`.

### Notes

1. All the Liquibase changesets in **masterdata/configuration** are only added temporarily for testing.
2. Backup of OpenMRS DB with pre-loaded CIEL Concepts and checksums of masterdata/configuration are maintained in [bahmni-scripts](https://github.com/Bahmni/bahmni-scripts/tree/master/demo/db-backups/1.0.0-lite) repository.
3. Whenever we are loading the CIEL zip for the first time, we need an OpenMRS restart to retire duplicate diagnosis concepts from CIEL.

### Transifex for Language Translations

Currently, both clinic-config and default-config share the same Transifex configuration. This needs to be fixed in the future by creating a separate configuration for clinic-config, because these are technically different config folders. They may have the same files right now, but as time progresses, they can deviate.

For now, we need to be careful to always add a **UNIQUE KEY** across default-config and clinic-config. Also note that, for the same Key+English string, the translation in other languages returned by Transifex will be the same across default-config or clinic-config, since the **memory** is the same for Transifex.

[Dev Notes for translating Bahmni](https://bahmni.atlassian.net/wiki/spaces/BAH/pages/41287695/Dev+Notes+for+Translating+Bahmni)
