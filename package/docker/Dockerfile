# Generate a pinned, checksum-verified Uganda hierarchy from the UBOS gazetteer.
FROM python:3.13-alpine AS ubos-address
WORKDIR /build
COPY scripts/build_uganda_address_hierarchy.py /build/build_uganda_address_hierarchy.py
RUN python /build/build_uganda_address_hierarchy.py --output /build/addresshierarchy.csv

FROM alpine:3.22

COPY openmrs /etc/bahmni_config/openmrs
COPY masterdata /etc/bahmni_config/masterdata
# Always replace the generic sample hierarchy with the verified Uganda hierarchy.
COPY --from=ubos-address /build/addresshierarchy.csv /etc/bahmni_config/masterdata/configuration/addresshierarchy/addresshierarchy.csv
COPY print-templates /etc/bahmni_config/print-templates
COPY web /etc/bahmni_config/web

COPY package/docker/start.sh start.sh
RUN chmod +x start.sh
CMD ["./start.sh"]
