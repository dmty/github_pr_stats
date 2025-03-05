#!/usr/bin/env python3
"""
Format PR statistics output as a Slack message and save as JSON payload
"""

import os
import json
from datetime import datetime

def format_stats_for_slack():
    """Read stats output and format as Slack message"""
    try:
        with open('stats_output.txt', 'r') as f:
            stats_content = f.read()
            
        # Extract date information from environment or filename
        last_month = os.environ.get('PERIOD') or datetime.now().strftime("%B %Y")
            
        # Create formatted Slack message
        slack_message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"PR Statistics for {last_month}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Monthly PR statistics report has completed."
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```{stats_content}```"
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
