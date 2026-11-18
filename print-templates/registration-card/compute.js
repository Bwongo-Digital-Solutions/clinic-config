const ADDRESS_EXT = 'http://fhir.openmrs.org/ext/address';

function addrExt(field) {
  return `Bundle.entry.first().resource.address.first()` +
    `.extension.where(url = '${ADDRESS_EXT}')` +
    `.extension.where(url = '${ADDRESS_EXT}#${field}').valueString`;
}

module.exports = {
  compute: async function ({ context, data, resolved, ValidationError, fhirPath }) {
    const patientBundle = resolved?.patient;
    const relativesBundle = resolved?.relatives;
    const profile = resolved?.patientProfile;

    // Uganda address hierarchy: Village → Parish → Subcounty → County → District → Country.
    const village = fhirPath(patientBundle, addrExt('address5')) ?? '';
    const parish = fhirPath(patientBundle, addrExt('address4')) ?? '';
    const subcounty = fhirPath(patientBundle, addrExt('address3')) ?? '';
    const county = fhirPath(patientBundle, "Bundle.entry.first().resource.address.first().state") ?? '';
    const district = fhirPath(patientBundle, "Bundle.entry.first().resource.address.first().district") ?? '';
    const country = fhirPath(patientBundle, "Bundle.entry.first().resource.address.first().country") ?? '';
    const composedAddress = [village, parish, subcounty, county, district, country]
      .filter(Boolean)
      .join(", ");

    return {
      patientId: fhirPath(patientBundle, "Bundle.entry.first().resource.identifier.where(use = 'official').first().value") ?? '',
      patientName: fhirPath(patientBundle, "Bundle.entry.first().resource.name.first().text") ?? '',
      birthDate: fhirPath(patientBundle, "Bundle.entry.first().resource.birthDate") ?? '',
      gender: fhirPath(patientBundle, "Bundle.entry.first().resource.gender") ?? '',
      phone: fhirPath(patientBundle, "Bundle.entry.first().resource.telecom.where(system = 'phone').first().value") ?? '',
      address: composedAddress || (fhirPath(patientBundle, "Bundle.entry.first().resource.address.first().text") ?? ''),
      registrationDate: profile?.patient?.auditInfo?.dateCreated ?? '',
      nextOfKinName: fhirPath(relativesBundle, "Bundle.entry.first().resource.name.first().text") ?? '',
      nextOfKinRelationship: fhirPath(relativesBundle, "Bundle.entry.first().resource.relationship.first().text") ?? '',
      photoUrl: `/openmrs/ws/rest/v1/patientImage?patientUuid=${context.patientUuid}`,
    };
  },
};
