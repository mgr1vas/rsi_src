# Contributing to RoadSafetyInsights

First off, thank you for considering contributing to RoadSafetyInsights! Our goal is to build a robust, secure, and highly effective platform, and community contributions are a huge part of making that happen.

The following is a set of guidelines for contributing to the repository.

## Getting Started

1. **Fork the repository** and clone it to your local environment.
2. **Create a new branch** for your feature or bug fix. We follow a standard naming convention:
   * Features: `feature/short-description`
   * Bug Fixes: `fix/issue-description`
3. **Make your changes** locally. Ensure your code is clean, commented where necessary, and adheres to the project's existing style.

## Security & Code Quality

Because this project handles infrastructure insights, maintaining strict security and quality standards is mandatory.

* **Automated Scanning:** All pull requests are automatically scanned via our CI/CD pipeline. Ensure your code passes all Static Application Security Testing (SAST) checks.
* **No Secrets:** Never commit API keys, passwords, or `.env` files. If your feature requires new environment variables, document them in a `.env.example` file.
* **Dynamic Checks:** Major feature branches may be subjected to Dynamic Application Security Testing (DAST) before merging to ensure runtime integrity.

## Pull Request Process

When you are ready to submit your changes:

1. **Test your code:** Ensure the application builds successfully locally and all existing functionalities remain intact.
2. **Update Documentation:** If your changes affect how the application is deployed, run locally, or configured, update the `README.md` accordingly.
3. **Open a Pull Request (PR):** Target the `main` (or `develop`, if active) branch. Provide a clear summary of what you changed and why.
4. **Pass CI/CD Checks:** Wait for the automated build, lint, and security workflows to complete. Fix any failing checks.
5. **Code Review:** The Lead Developer or another core maintainer will review your PR. We may request modifications to align with our architectural or security standards before approving the merge.

## Reporting Bugs

If you discover a bug, please check the existing issues to ensure it hasn't already been reported. If it is new, open an issue including:

* **Description:** A clear and concise description of what the bug is.
* **Steps to Reproduce:** Exact steps to trigger the behavior.
* **Expected vs. Actual Behavior:** What you expected to happen, and what actually happened.
* **Environment:** Device, OS, browser, or server configuration details.

## Proposing Features

We are always open to new ideas to improve RoadSafetyInsights! To propose a feature, open an issue and include:

* The core problem you are trying to solve.
* Your proposed solution or architecture.
* Any alternative approaches you have considered.

---

Thank you for your time, effort, and code! Let's build something impactful.
