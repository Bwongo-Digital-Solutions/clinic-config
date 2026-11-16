#!/bin/sh
set -eu

SOURCE_DIR="/etc/bahmni_config"
CONFIG_VOLUME_DIR="/usr/local/bahmni_config"

echo "Seeding Bahmni configuration into ${CONFIG_VOLUME_DIR}"
mkdir -p "${CONFIG_VOLUME_DIR}"

# Copy the contents, not the parent directory. The config volume is shared
# with OpenMRS, Bahmni Web, reports, and the template service.
cp -a "${SOURCE_DIR}/." "${CONFIG_VOLUME_DIR}/"

echo "Bahmni configuration is ready."
exec tail -f /dev/null
