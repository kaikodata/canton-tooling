# Remove files you don't use from your template directories (canton-val & canton-sv) :

*   If you used a postgresql which is external to kubernetes, remove *postgres*.yaml files
*   If you don't use cloud KMS for participant, remove *kms*.yaml files

# Uncompress here the Helm variables from the splice release you want to use :
```bash
cp splice-0.4.0/splice-node/examples/sv-helm/* tmpl/splice-archive
```

# Then update the files in your template directory with latest version :
```bash
./refresh_values_from_splice_release.sh tmpl/splice-archive/ tmpl/canton-sv/
```

It would only copies files which changes and display a diff of changes.
