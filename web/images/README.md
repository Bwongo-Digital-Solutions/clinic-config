# Uganda clinic branding assets

Place the clinic's approved image assets in this directory, keeping filenames and
extensions stable so that the Bahmni configuration can reference them consistently.

Suggested structure:

```
web/images/
  logo/
    clinic-logo.png
    clinic-logo.svg
    clinic-logo-white.png
  login/
    login-background.jpg
  registration/
    registration-logo.png
  favicon/
    favicon.png
```

## How these files are served

The Bahmni Lite `bahmni-web` service mounts the shared configuration volume at
`/usr/local/apache2/htdocs/bahmni_config/`. The config image seeds this directory
from `/etc/bahmni_config`, including this `web/images` folder.

Consequently, a file at:

`web/images/logo/clinic-logo.png`

is available to the browser at:

`/bahmni_config/web/images/logo/clinic-logo.png`

Use this URL prefix in Bahmni configuration (including `whiteLabel.json`) unless
the web-server mapping is deliberately changed. Do not assume that
`/bahmni/images/` points to this directory.

Add the actual image files alongside this README. Update the relevant configuration
references to the exact committed filenames; avoid renaming assets without updating
those references.
