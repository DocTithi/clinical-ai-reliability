# Contributing

Contributions are welcome.

## Principles

- Use synthetic or properly de-identified/public data in repository examples.
- Do not add patient-identifying information.
- Do not present protocol metrics as medical safety certification.
- Add tests for behavioral changes.
- Document assumptions and limitations.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
```

## Pull requests

Please include the problem being solved, proposed behavior, tests, scientific assumptions, and whether the schema changes.

Large protocol changes should begin as a GitHub issue so their semantics can be discussed before implementation.
