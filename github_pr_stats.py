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
from tqdm import tqdm


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
    
    # Create date filtering group
    date_group = parser.add_mutually_exclusive_group()
    
    # Option 1: Use days (default)
    date_group.add_argument(
        "-d", "--days",
        type=int,
        default=90,
        help="Number of days to analyze (default: 90)"
    )
    
    # Option 2: Use specific date range (--start-date and --end-date are not mutually exclusive)
    date_group.add_argument(
        "--start-date",
        type=lambda d: datetime.strptime(d, '%Y-%m-%d').replace(tzinfo=timezone.utc),
        help="Start date for PR analysis (format: YYYY-MM-DD)"
    )
    
    # End date is not in the mutually exclusive group
    parser.add_argument(
        "--end-date",
        type=lambda d: datetime.strptime(d, '%Y-%m-%d').replace(tzinfo=timezone.utc),
        help="End date for PR analysis (format: YYYY-MM-DD, defaults to today)"
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


def analyze_prs(repos: List[Repository], start_date: datetime, end_date: datetime = None) -> Dict[str, PRStats]:
    """
    Analyze PRs from all repositories and generate statistics.
    
    Args:
        repos: List of repositories to analyze
        start_date: Starting date for PR analysis
        end_date: Ending date for PR analysis (optional)
        
    Returns:
        Dictionary mapping usernames to their PR statistics
    """
    user_stats: Dict[str, PRStats] = {}
    total_prs_count = 0
    
    # First pass to count total PRs for progress bar
    print("\nCounting PRs...")
    for repo in tqdm(repos, desc="Scanning repositories"):
        try:
            pulls = repo.get_pulls(state='all', sort='updated', direction='desc')
            for pr in pulls:
                pr_updated = datetime.strptime(pr.updated_at.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                
                # Skip if PR is outside date range
                if pr_updated < start_date:
                    break
                if end_date and pr_updated > end_date:
                    continue
                    
                total_prs_count += 1
        except GithubException as e:
            print(f"\nError accessing PRs in {repo.name}: {e}")
            continue
    
    # Second pass to analyze PRs with progress bar
    print("\nAnalyzing PRs...")
    with tqdm(total=total_prs_count, desc="Processing PRs") as pbar:
        for repo in repos:
            try:
                pulls = repo.get_pulls(state='all', sort='updated', direction='desc')
                for pr in pulls:
                    pr_updated = datetime.strptime(pr.updated_at.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                    
                    # Skip if PR is outside date range
                    if pr_updated < start_date:
                        break
                    if end_date and pr_updated > end_date:
                        continue
                    
                    username = pr.user.login
                    if username not in user_stats:
                        user_stats[username] = PRStats()
                    
                    if pr.state == 'open':
                        user_stats[username].open += 1
                    elif pr.merged:
                        user_stats[username].merged += 1
                    else:
                        user_stats[username].closed += 1
                    
                    user_stats[username].total_lines += pr.additions + pr.deletions
                    user_stats[username].total_prs += 1
                    pbar.update(1)
                        
            except GithubException as e:
                print(f"\nError accessing PRs in {repo.name}: {e}")
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
        
        # Determine date range for analysis
        end_date = None
        if args.start_date:
            # Use specific date range
            start_date = args.start_date
            
            if args.end_date:
                end_date = args.end_date
            else:
                # Default end date is today
                end_date = datetime.now(timezone.utc).replace(
                    hour=23, minute=59, second=59, microsecond=999999
                )
            
            print(f"\nAnalyzing PRs from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        else:
            # Use days (default approach)
            start_date = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(days=args.days)
            
            print(f"\nAnalyzing PRs for the last {args.days} days...")
            
            # Ensure end_date is set for consistency
            end_date = datetime.now(timezone.utc).replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
        
        print("\nFetching repositories...")
        repos = get_repos(g, args.org_name)
        if not repos:
            print("No repositories found or error accessing organization.")
            return
            
        print(f"Found {len(repos)} repositories")
        
        # Analyze PRs with date range
        stats = analyze_prs(repos, start_date, end_date)
        
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

