#!/usr/bin/env python3
"""
GitHub Pull Request Statistics Generator

This script analyzes pull requests across all repositories in a GitHub organization
for the last 3 months and generates statistics per user.
"""

import os
import argparse
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from github import Github, GithubException
from github.PullRequest import PullRequest
from github.Repository import Repository
from dotenv import load_dotenv


class PRStats:
    def __init__(self):
        self.open = 0
        self.merged = 0
        self.closed = 0
        self.total_lines = 0
        self.total_prs = 0

    def __str__(self) -> str:
        return f"Open: {self.open}, Merged: {self.merged}, Closed: {self.closed}"

    @property
    def avg_lines_per_pr(self) -> float:
        """Calculate average lines changed per PR."""
        if self.total_prs == 0:
            return 0.0
        return round(self.total_lines / self.total_prs, 1)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    # Load environment variables
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description="Generate PR statistics for a GitHub organization"
    )
    parser.add_argument(
        "org_name",
        nargs='?',
        default=os.getenv('DEFAULT_ORG'),
        help="Name of the GitHub organization (can be set in .env file)"
    )
    parser.add_argument(
        "-d", "--days",
        type=int,
        default=90,
        help="Number of days to analyze (default: 90)"
    )
    return parser.parse_args()


def get_repos(g: Github, org_name: str) -> List[Repository]:
    """
    Fetch all repositories (both public and private) from the organization.
    
    Args:
        g: GitHub instance
        org_name: Name of the organization
        
    Returns:
        List of Repository objects
    """
    try:
        org = g.get_organization(org_name)
        return list(org.get_repos(type='all'))  # 'all' includes private repos
    except GithubException as e:
        print(f"Error accessing organization {org_name}: {e}")
        return []


def analyze_prs(repos: List[Repository], since_date: datetime) -> Dict[str, PRStats]:
    """
    Analyze PRs from all repositories and generate statistics.
    
    Args:
        repos: List of repositories to analyze
        since_date: Starting date for PR analysis
        
    Returns:
        Dictionary mapping usernames to their PR statistics
    """
    user_stats: Dict[str, PRStats] = {}
    
    for repo in repos:
        try:
            pulls = repo.get_pulls(state='all', sort='updated', direction='desc')
            for pr in pulls:
                # Ensure both datetimes are UTC
                pr_updated = datetime.strptime(pr.updated_at.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                if pr_updated < since_date:
                    break
                    
                username = pr.user.login
                if username not in user_stats:
                    user_stats[username] = PRStats()
                
                # Update PR counts
                if pr.state == 'open':
                    user_stats[username].open += 1
                elif pr.merged:
                    user_stats[username].merged += 1
                else:
                    user_stats[username].closed += 1
                
                # Update lines changed statistics
                user_stats[username].total_lines += pr.additions + pr.deletions
                user_stats[username].total_prs += 1
                    
        except GithubException as e:
            print(f"Error accessing PRs in {repo.name}: {e}")
            continue
            
    return user_stats


def display_stats(stats: Dict[str, PRStats]) -> None:
    """
    Display PR statistics in a formatted table, sorted by number of merged PRs.
    
    Args:
        stats: Dictionary mapping usernames to their PR statistics
    """
    if not stats:
        print("No PR statistics found.")
        return
        
    print("\nPull Request Statistics per User (sorted by merged PRs):")
    print("-" * 95)
    print(f"{'Username':<20} {'Open':<8} {'Merged':<8} {'Closed':<8} {'Total Lines':<12} {'Avg Lines/PR':<12}")
    print("-" * 95)
    
    # Sort by number of merged PRs in descending order
    sorted_stats = sorted(
        stats.items(),
        key=lambda x: (x[1].merged, x[0]),  # Sort by merged count, then username
        reverse=True  # Descending order
    )
    
    total_lines = 0
    total_prs = 0
    
    for username, pr_stats in sorted_stats:
        total_lines += pr_stats.total_lines
        total_prs += pr_stats.total_prs
        print(
            f"{username:<20} {pr_stats.open:<8} {pr_stats.merged:<8} {pr_stats.closed:<8} "
            f"{pr_stats.total_lines:<12} {pr_stats.avg_lines_per_pr:<12}"
        )
    
    print("-" * 95)
    avg_lines = round(total_lines / total_prs, 1) if total_prs > 0 else 0
    print(f"{'TOTAL':<20} {'':<8} {'':<8} {'':<8} {total_lines:<12} {avg_lines:<12}")


def get_github_instance() -> Optional[Github]:
    """
    Create GitHub instance using token from .env file.
    """
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN not found in environment or .env file")
        print("Please copy .env.example to .env and set your GitHub token")
        print("You can generate a token at: https://github.com/settings/tokens")
        print("Required scopes: repo, read:org")
        return None
    
    try:
        return Github(token)
    except Exception as e:
        print(f"Error authenticating with GitHub: {e}")
        return None


def main():
    """Main function to run the script."""
    args = parse_arguments()
    
    try:
        g = get_github_instance()
        if not g:
            print("Failed to authenticate with GitHub")
            return
            
        # Calculate date based on provided days
        since_date = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(days=args.days)
        
        print(f"\nAnalyzing PRs for the last {args.days} days...")
        
        # Get all repositories
        repos = get_repos(g, args.org_name)
        if not repos:
            print("No repositories found or error accessing organization.")
            return
            
        # Analyze PRs
        stats = analyze_prs(repos, since_date)
        
        # Display results
        display_stats(stats)
        
    except GithubException as e:
        print(f"GitHub API error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'g' in locals():
            g.close()


if __name__ == "__main__":
    main()

