# Contributing

This project welcomes reproducible fixes and practical teaching improvements.

1. Open an issue explaining the problem, expected behavior, and a small synthetic example.
2. Fork the repository and create a branch for one focused change.
3. Run `python -m unittest -v test_data.py`.
4. If changing a business rule, update the dictionary, SQL/DAX, and relevant tests together.
5. Submit a pull request with what changed and exactly how it was checked.

Keep changes small enough to review. Do not upload real customer/employer data,
passwords, API keys, access tokens, or private screenshots. Use fictional examples.
Avoid adding a dependency unless it solves a clear problem.

When reporting Fabric issues, include the runtime version, relevant cell, sanitized
error text, and expected versus actual result. Local Python tests cannot establish
that a Fabric notebook, semantic model, or access policy works in a tenant.

AI-assisted contributions are welcome when their author reviews the changes,
discloses material limitations, and verifies the claimed results.

By contributing, you agree that your contributions are licensed under this
repository's MIT license. Be respectful, constructive, and specific in discussions.
