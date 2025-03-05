# GitHub Actions Setup

To set up the monthly PR stats GitHub Action, you'll need to configure the following secrets in your GitHub repository:

1. Go to your GitHub repository
2. Click on `Settings` > `Secrets and variables` > `Actions`
3. Add the following secrets:

## Required Secrets

- `PR_STATS_TOKEN`: A GitHub Personal Access Token with `repo` and `read:org` permissions
- `ORG_NAME`: Your GitHub organization name
- `SLACK_BOT_TOKEN`: Slack Bot token from your Slack app
- `SLACK_CHANNEL_ID`: The ID of the Slack channel to post to

## Setting up Slack Integration

1. Create a new Slack app at https://api.slack.com/apps
2. Add the following Bot Token Scopes:
   - `chat:write`
   - `chat:write.public` (if posting to public channels)
3. Install the app to your workspace
4. Copy the Bot User OAuth Token to the `SLACK_BOT_TOKEN` secret
5. Get your channel ID by right-clicking on a channel and selecting "Copy Link"

## Manual Triggering

You can manually trigger the workflow by:
1. Going to the "Actions" tab in your repository
2. Selecting "Monthly GitHub PR Stats" workflow
3. Clicking "Run workflow"
