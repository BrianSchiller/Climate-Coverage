import json
from collections import defaultdict
from datetime import datetime
import numpy as np
import pandas as pd

import plots
import settings

def detect_outliers_and_cap(data):
    """Detect outliers using the IQR method and cap them at Q3 + 2 * IQR."""
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    upper_bound = q3 + 1.5 * iqr
    lower_bound = q1 - 1.5 * iqr
    outliers = sum(1 for x in data if x > upper_bound and x > 1)
    capped_data = [min(max(x, lower_bound), max(1, upper_bound)) for x in data]
    return capped_data, outliers


def aggregate_newspaper_weekly_average():
    file_path = r"data\article_keyword_count.json"
    with open(file_path) as r:
            data = json.load(r)

    results = {}
    outlier_counts = defaultdict(int)

    # Collect all counts by topic across all newspapers and weeks
    global_topic_data = defaultdict(list)
    for newspaper, articles in data.items():
        for article, topics in articles.items():
            for topic, count in topics.items():
                global_topic_data[topic].append(count)

    # Cap outliers globally for each topic and count them
    capped_topic_data = {}
    for topic, counts in global_topic_data.items():
        capped_data, outliers = detect_outliers_and_cap(counts)
        capped_topic_data[topic] = capped_data
        outlier_counts[topic] += outliers

    # Helper function to get the year-week from the filename
    def get_year_week(filename):
        date_str = filename.split("T")[0]  # Extract date
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return "-".join(map(str, date_obj.isocalendar()[:2]))  # (year, week)

    for newspaper, articles in data.items():
        weekly_data = defaultdict(lambda: defaultdict(list))
        article_counts = defaultdict(int)

        # Organize data by week
        for article, topics in articles.items():
            year_week = get_year_week(article)
            article_counts[year_week] += 1
            for topic, count in topics.items():
                capped_count = min(count, max(capped_topic_data[topic]))
                weekly_data[year_week][topic].append(capped_count)

        # Calculate averages
        weekly_averages = {}
        for year_week, topics in weekly_data.items():
            averages = {
                topic: sum(counts) / len(counts) for topic, counts in topics.items()
            }
            weekly_averages[year_week] = {
                "averages": averages,
                "article_count": article_counts[year_week]
            }

        results[newspaper] = weekly_averages

    path = "data/article_keyword_per_week.json"
    with open(path, 'w', encoding='utf-8') as count_file:
        json.dump(results, count_file, indent=4)

    return results, outlier_counts


def aggregate_subreddit_weekly_average():
    # Dictionary to store the aggregated data for each subreddit
    aggregated_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))  # Includes label type (post or comment)
    post_counts_per_week = defaultdict(lambda: defaultdict(int))  # Store the number of posts per week
    outlier_counts = defaultdict(int)

    # Aggregated data for outlier detection (for all weeks)
    all_label_counts = defaultdict(list)  # For each label, store all counts across weeks
    
    # Loop over each JSON file in the subreddit folder
    for subreddit in settings.SUBREDDITS:
        file_path = f"reddit/{subreddit}_processed.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            posts = json.load(f)
            
            for post in posts:
                # Parse the date
                created_date = datetime.strptime(post['Created'], '%Y-%m-%d %H:%M:%S')
                year, week_num, _ = created_date.isocalendar()  # Get ISO year and week number
                
                # Increment the number of posts for the week
                post_counts_per_week[subreddit][(year, week_num)] += 1
                
                # Aggregating labels for the post itself
                for label, count in post['labels'].items():
                    aggregated_data[subreddit][(year, week_num)]['post'][label] += count
                    all_label_counts[label].append(count)  # Collecting data for outlier detection
                
                # Aggregating labels for the comments
                for label, count in post['comment_labels'].items():
                    aggregated_data[subreddit][(year, week_num)]['comment'][label] += count
                    all_label_counts[label].append(count)  # Collecting data for outlier detection
    
    # Now detect outliers and apply the capping for each label across all posts and comments
    final_data = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))  # Subreddit -> Week -> label_type -> label count
    
    # Apply outlier detection and capping for all labels
    for label, counts in all_label_counts.items():
        capped_counts, outliers = detect_outliers_and_cap(counts)
        outlier_counts[label] += outliers
        all_label_counts[label] = capped_counts  # Store the capped counts back
    
    # Now process each subreddit and week
    for subreddit, subreddit_data in aggregated_data.items():
        for (year, week), label_data in subreddit_data.items():
            week_key = f"{year}-W{week}"  # Week in 'YYYY-Www' format
            post_count = post_counts_per_week[subreddit][(year, week)]
            if post_count == 0:
                continue  # Skip weeks with no posts
            
            # Add the post count as the total number of posts for the week
            final_data[subreddit][week_key]["post_count"] = post_count

            # Process each label (both post and comment) for outlier detection and averages
            for label_type, labels in label_data.items():
                for label, total_count in labels.items():
                    # Apply capped count (after outlier detection)
                    capped_count = min(total_count, max(all_label_counts[label]))  # Use the capped count for this label
                    # Calculate average per post
                    final_data[subreddit][week_key][label_type][label] = capped_count / post_count  # Average per post
    
    # Write the dictionary to a JSON file
    path = "reddit/reddit_keyword_per_week.json"
    with open(path, 'w', encoding='utf-8') as count_file:
        json.dump(final_data, count_file, indent=4)

    return final_data, outlier_counts

# Call the function
newspaper_weekly_averages, news_outlier_counts = aggregate_newspaper_weekly_average()
reddit_weekly_averages, reddit_outlier_counts = aggregate_subreddit_weekly_average()

# Pretty print results
import pprint

# print("\nOutlier Counts:")
# pprint.pprint(news_outlier_counts)
# pprint.pprint(reddit_outlier_counts)

plots.plot_keyword_count_per_week()
plots.plot_subreddit_keyword_count_per_week()
