# GitHub Actions Secrets Configuration

This document describes the secrets required for the CI/CD pipeline.

## Required Secrets

### PYPI_API_TOKEN
- **Purpose**: Used to authenticate with PyPI for package deployment
- **How to get**: 
  1. Go to [PyPI](https://pypi.org/) and log in
  2. Navigate to Account Settings > API tokens
  3. Create a new API token with the "Upload" scope
  4. Copy the token value
- **Where to add**: GitHub repository Settings > Secrets > Actions > New repository secret
- **Name**: `PYPI_API_TOKEN`
- **Value**: Your PyPI API token

## Optional Secrets

### OPENROUTER_API_KEY
- **Purpose**: Used for testing the application with actual API calls
- **How to get**: 
  1. Go to [OpenRouter.ai](https://openrouter.ai/)
  2. Sign up and navigate to API Keys
  3. Create a new API key
  4. Copy the key
- **Where to add**: GitHub repository Settings > Secrets > Actions > New repository secret
- **Name**: `OPENROUTER_API_KEY`
- **Value**: Your OpenRouter API key

## Setting Up Secrets

1. Go to your GitHub repository
2. Click on "Settings" tab
3. Click on "Secrets and variables" > "Actions"
4. Click "New repository secret"
5. Add the secret name and value
6. Click "Add secret"

## Using Secrets in Workflows

Secrets are automatically available as environment variables in GitHub Actions workflows:

```yaml
env:
  TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
```

## Security Best Practices

- Never hardcode secrets in workflow files
- Use GitHub's built-in secret masking
- Rotate secrets regularly
- Limit secret access to only necessary workflows
- Use organization-level secrets for multiple repositories
