import json
from collections import defaultdict
from datetime import datetime
import numpy as np

import plots

def detect_outliers_and_cap(data):
    """Detect outliers using the IQR method and cap them at Q3 + 1.5 * IQR."""
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    upper_bound = q3 + 1.5 * iqr
    outliers = sum(1 for x in data if x > upper_bound and x > 1)
    capped_data = [min(x, max(1, upper_bound)) for x in data]
    return capped_data, outliers


def aggregate_weekly_averages():
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

# Call the function
weekly_averages, outlier_counts = aggregate_weekly_averages()

# Pretty print results
import pprint

print("\nOutlier Counts:")
pprint.pprint(outlier_counts)

plots.plot_keyword_count_per_week()
