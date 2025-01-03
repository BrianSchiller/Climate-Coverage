import praw
import json
from datetime import datetime
from praw.models import Submission

# Set up the Reddit instance with your app credentials
reddit = praw.Reddit(
    client_id="1R_d_OyW9Fo3stj_fKG0tw",
    client_secret="oJ3xErpdiyBIMq6UxaB6GVyOhHqnbg",
    user_agent="student_climate_change_project"  # A description like 'my_script/0.1 by username'
)

posts = []

# Example: Get 5 posts from a subreddit (e.g., Python subreddit)
subreddit = reddit.subreddit('climate')
for submission in subreddit.controversial(time_filter="year"):
    submission: Submission

    post = {
        "ID": submission.id,
        "Title": submission.title,
        "Author": submission.author.name if submission.author is not None else "Unknown",
        "Upvotes": submission.score,
        "Created": datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
        "Content": submission.selftext,
        "Processed_Content": "",
        "Selfpost": submission.is_self,
        "URL": submission.url,
        "CommCount": submission.num_comments,
        "Comments": []
    }

    submission.comments.replace_more(limit=0)
    comments = submission.comments.list()

    # Get the top 20 comments
    top_comments = sorted(comments, key=lambda c: c.score, reverse=True)[:20]

    for comment in top_comments:
        post["Comments"].append(
            {
                "ID": comment.id,
                "Author": comment.author.name if comment.author is not None else "Unknown",
                "Upvotes": comment.score,
                "Content": comment.body
            }
        )

    print(post)

    posts.append(post)

file_name = f'reddit/climate.json'

with open(file_name, 'w') as json_file:
        json.dump(posts, json_file, indent=4)

