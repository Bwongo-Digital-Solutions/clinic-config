# Uganda address hierarchy

The generated `addresshierarchy.csv` contains one complete path per village:

`Uganda, District, County, Subcounty, Parish, Village`

Source: Uganda Bureau of Statistics (UBOS), *Administrative units of Uganda* gazetteer snapshot dated 2026-11-13, published by Uganda Open Data. The pinned source file is 10,573,277 bytes and has SHA-256:

`effbc52af0a37985acb205f3217f10014c32a8c9d6fca920ee942d38bea14b5c`

The dataset has 71,679 village records and is licensed CC BY 4.0. Attribution: Uganda Bureau of Statistics (UBOS); dataset publisher: Uganda Open Data.

The image build downloads this pinned snapshot, verifies its checksum, validates all ancestry columns and row count, then converts it into Bahmni's six-level, headerless hierarchy format. The import uses `<wipe>true</wipe>` to replace the existing address-hierarchy entries (including the incorrect India hierarchy). This wipe is limited to the address-hierarchy data; it does not delete patient records, visits, encounters, or other OpenMRS clinical data.

To refresh the snapshot in future, update the source URL, SHA-256, expected row count, and this attribution note together after reviewing the new UBOS release.
