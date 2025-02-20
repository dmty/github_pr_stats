# GitHub PR Statistics

A tool to analyze pull requests across all repositories in a GitHub organization.

## Prerequisites

1. Generate a GitHub Personal Access Token:
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo`, `read:org`
   - Copy the generated token

2. Set the token as an environment variable:
   ```bash
   export GITHUB_TOKEN='your_token_here'
   ```

## Setup

1. Create your environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit .env file with your GitHub token:
   ```bash
   # Generate token at https://github.com/settings/tokens
   # Required scopes: repo, read:org
   nano .env
   ```

3. Make the setup script executable:
   ```bash
   chmod +x setup.sh
   ```

4. Run the setup script to create and configure the virtual environment:
   ```bash
   ./setup.sh
   ```

## Usage

With the virtual environment activated, run:
```bash
# Using organization from command line
python github_pr_stats.py <organization-name>

# Or using DEFAULT_ORG from .env file
python github_pr_stats.py
```

To deactivate the virtual environment when done:
```bash
deactivate
```
````
