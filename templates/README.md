# Templates

```
.
├── ammos-config.template.yaml
├── ammos-cubs-ait.template.yaml
├── ammos-cubs-alb.template.yaml
├── ammos-cubs-cognito.template.yaml
├── ammos-cubs-editor.template.yaml
├── ammos-cubs-logging.template.yaml
├── ammos-cubs.entry-main.template.yaml             # Entry Template for quick-create link
├── ammos-cubs.main.template.yaml
├── ammos-cubs.preconfig.template.yaml
├── ammos-cubs.testing.template.yaml
├── ast-data.template.yaml
└── ast-iam-roles.template.yaml

```


## Notes

- **ammos-cubs.entry-main.template.yaml**: The entry template is generated from a script in `scripts/entry`. It is an adaptor for the main stack for parameters passed in as a blob: either directly through command line cloudformation builds or through the AWS cloudformation quick-create link.
