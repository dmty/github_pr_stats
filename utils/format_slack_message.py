#!/usr/bin/env python3
"""Format PR statistics output as a Slack message and save as JSON payload"""

import os
import json
import re
from datetime import datetime

def format_stats_for_slack():
    """Read stats output and format as Slack message"""
    try:
        with open('stats_output.txt', 'r') as f:
            stats_content = f.read()
        
        # Extract the date range and repository count
        date_match = re.search(r'PR Statistics from (\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})', stats_content)
        repo_count_match = re.search(r'Analyzed (\d+) repositories', stats_content)
        
        date_range = f"{date_match.group(1)} to {date_match.group(2)}" if date_match else "custom period"
        repo_count = repo_count_match.group(1) if repo_count_match else "multiple"
        
        # Find the table in the output (everything after "sorted by merged PRs")
        table_match = re.search(r'Pull Request Statistics per User.*?\n(.*)', stats_content, re.DOTALL)
        if table_match:
            table_content = table_match.group(1)
        else:
            table_content = stats_content
            
        # Get month name for title
        month_name = os.environ.get('PERIOD') or datetime.now().strftime("%B %Y")
            
        # Create formatted Slack message
        slack_message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"PR Statistics for {month_name}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn", 
                        "text": f"*Period:* {date_range}\n*Repositories analyzed:* {repo_count}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "```\n" + table_content + "```"
                    }
                }
            ]
        }
        
        # Save as JSON file for the GitHub Action
        with open('slack_payload.json', 'w') as f:
            json.dump(slack_message, f)
            
        print("Slack message payload created successfully.")
        
    except Exception as e:
        print(f"Error formatting stats for Slack: {e}")
        # Create a simple error message
        slack_message = {
            "text": f"Error generating PR statistics: {e}"
        }
        with open('slack_payload.json', 'w') as f:
            json.dump(slack_message, f)

if __name__ == "__main__":
    format_stats_for_slack()
