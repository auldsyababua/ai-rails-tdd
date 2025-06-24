# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of AI Rails TDD seriously. If you have discovered a security vulnerability, please follow these steps:

### 1. Do NOT Create a Public Issue

Security vulnerabilities should not be reported through public GitHub issues.

### 2. Email Us Directly

Please email security concerns to: [INSERT SECURITY EMAIL]

Include the following information:
- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### 3. Response Time

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

## Security Considerations

### API Keys
- Never commit API keys to the repository
- Always use environment variables for sensitive data
- Rotate keys regularly

### Test Execution
- All generated code runs in isolated environments
- Test execution has configurable timeouts
- File system access is restricted

### Dependencies
- We regularly update dependencies for security patches
- Use `pip audit` to check for known vulnerabilities

## Disclosure Policy

When we receive a security report, we will:

1. Confirm the problem and determine affected versions
2. Audit code to find similar problems
3. Prepare fixes for all supported releases
4. Release patches as soon as possible

We appreciate your efforts to responsibly disclose your findings and will make every effort to acknowledge your contributions.