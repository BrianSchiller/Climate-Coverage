import praw
import json
from datetime import datetime, timedelta
from praw.models import Submission
import logging
import os

# Set up the Reddit instance with your app credentials
reddit = praw.Reddit(
    client_id="1R_d_OyW9Fo3stj_fKG0tw",
    client_secret="oJ3xErpdiyBIMq6UxaB6GVyOhHqnbg",
    user_agent="student_climate_change_project"  # A description like 'my_script/0.1 by username'
)

def fetch_top_comments(submission, top_n=30):
    """Fetch top comments from a submission."""
    try:
        submission.comments.replace_more(limit=0)
        comments = [comment for comment in submission.comments.list() if isinstance(comment, praw.models.Comment)]
        top_comments = sorted(comments, key=lambda c: c.score, reverse=True)[:top_n]
        return [
            {
                "ID": comment.id,
                "Author": comment.author.name if comment.author else "Unknown",
                "Upvotes": comment.score,
                "Content": comment.body
            }
            for comment in top_comments
        ]
    except Exception as e:
        logging.error(f"Error fetching comments for submission {submission.id}: {e}")
        return []


def fetch_posts_last_n_months(subreddit_name, months=3, limit=1000):
    """Fetch posts from the last N months."""
    posts = []
    try:
        subreddit = reddit.subreddit(subreddit_name)
        time_cutoff = datetime.now() - timedelta(days=30 * months)

        for submission in subreddit.top(time_filter="year", limit=limit):
            post_date = datetime.fromtimestamp(submission.created_utc)
            if post_date >= time_cutoff:
                posts.append({
                "ID": submission.id,
                "Title": submission.title,
                "Author": submission.author.name if submission.author else "Unknown",
                "Upvotes": submission.score,
                "Created": datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                "Content": submission.selftext,
                "Processed_Content": "",
                "Selfpost": submission.is_self,
                "URL": submission.url,
                "CommCount": submission.num_comments,
                "Comments": fetch_top_comments(submission)
            })
            else:
                print("Skipped old post")
                # Stop processing older posts to save time
                continue

        logging.info(f"Fetched {len(posts)} posts from r/{subreddit_name} in the last {months} months.")
    except Exception as e:
        logging.error(f"Error fetching posts from subreddit {subreddit_name}: {e}")
    return posts

def fetch_posts(subreddit_name, time_filter="year", limit=100):
    """Fetch posts from a subreddit."""
    posts = []
    try:
        subreddit = reddit.subreddit(subreddit_name)
        for submission in subreddit.controversial(time_filter=time_filter, limit=limit):
            post = {
                "ID": submission.id,
                "Title": submission.title,
                "Author": submission.author.name if submission.author else "Unknown",
                "Upvotes": submission.score,
                "Created": datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                "Content": submission.selftext,
                "Processed_Content": "",
                "Selfpost": submission.is_self,
                "URL": submission.url,
                "CommCount": submission.num_comments,
                "Comments": fetch_top_comments(submission)
            }
            posts.append(post)
            logging.info(f"Fetched post {submission.id}")
    except Exception as e:
        logging.error(f"Error fetching posts from subreddit {subreddit_name}: {e}")
    return posts

def save_data(posts, file_name):
    """Save posts data to a JSON file."""
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, 'w') as json_file:
        json.dump(posts, json_file, indent=4)

if __name__ == "__main__":
    subreddit_name = "ClimateActionPlan"
    posts = fetch_posts_last_n_months(subreddit_name)
    file_name = f'reddit/{subreddit_name}.json'
    save_data(posts, file_name)

