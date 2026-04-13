# Security Policy

## Supported scope

This project currently targets local development and demo usage.

Important notes:

- It depends on a third-party LLM API
- The current in-memory task execution model is not intended for high-concurrency production deployment
- OCR for scanned PDFs is not included

## Reporting a vulnerability

If you discover a security issue, please do not post full exploit details in a public issue.

Recommended approach:

- Contact the repository maintainer privately first
- Provide a clear reproduction path
- Describe the impact and affected area
- Include a suggested fix if possible

## Secrets handling

- Never commit a real API key
- Never commit `.env`
- Rotate any secret immediately if you think it may have been exposed
- Do not expose secrets in logs, screenshots, sample responses, or recorded demos
