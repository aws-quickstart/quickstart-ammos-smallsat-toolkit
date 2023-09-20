# Templates

```
.
├── ammos-config.template.yaml
├── ast-ait.template.yaml
├── ast-alb.template.yaml
├── ast-cognito.template.yaml
├── ast-editor.template.yaml
├── ast-logging.template.yaml
├── ast.entry-main.template.yaml             # Entry Template for quick-create link
├── ast.main.template.yaml
├── ast.preconfig.template.yaml
├── ast.testing.template.yaml
├── ast-data.template.yaml
└── ast-iam-roles.template.yaml

```


## Notes

- **ammos-cubs.entry-main.template.yaml**: The entry template is generated from a script in `scripts/entry`. It is an adaptor for the main stack for parameters passed in as a blob: either directly through command line cloudformation builds or through the AWS cloudformation quick-create link.
