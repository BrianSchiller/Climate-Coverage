import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import os
import json
from pathlib import Path
import seaborn as sns
import pandas as pd


def plot_newspaper_keyword_count(data, cols = 3):
    # Number of newspapers and labels
    newspapers = list(data.keys())
    labels = list(next(iter(data.values()))["labels"].keys())
    num_newspapers = len(newspapers)

    # Use a colormap with more distinct colors
    colors = plt.cm.tab20(np.linspace(0, 1, len(labels)))
    label_colors = {label: color for label, color in zip(labels, colors)}

    # Determine grid layout
    rows = (num_newspapers + cols - 1) // cols  # Calculate rows needed
    fig, axs = plt.subplots(rows, cols, figsize=(16, rows * 5), sharex=False)

    # Flatten axs to a 1D array for easy iteration
    axs = axs.flatten()

    for i, newspaper in enumerate(newspapers):
        counts = [data[newspaper]["labels"][label] for label in labels]
        x = np.arange(len(labels))
        bar_colors = [label_colors[label] for label in labels]
        axs[i].bar(x, counts, color=bar_colors, edgecolor='black')

        # Customize each subplot
        axs[i].set_title(f"{newspaper}", fontsize=14, pad=15)
        axs[i].set_ylabel("Mentions", fontsize=12)
        axs[i].set_xticks([])  # Remove x-tick labels to avoid overlap
        axs[i].grid(axis='y', linestyle='--', alpha=0.7)

        # Add the number of articles below the bar graph
        num_articles = data[newspaper]["num_articles"]
        axs[i].text(0.5, -0.2, f'Articles: {num_articles}', ha='center', va='center', fontsize=12, transform=axs[i].transAxes)

    # Hide unused subplots
    for ax in axs[num_newspapers:]:
        ax.axis('off')

    # Add a legend
    handles = [plt.Line2D([0], [0], color=color, lw=4) for color in colors]
    fig.legend(handles, labels, loc='upper center', ncol=4, fontsize=12, title="Labels", bbox_to_anchor=(0.5, 0.95))

    fig.suptitle("Keyword count per newspaper", fontsize=16, fontweight='bold', y=0.98)

    # Adjust spacing between subplots
    plt.subplots_adjust(hspace=0.5, wspace=0.3, top=0.85, bottom=0.1)

    # Show the plot
    path = "data/newspaper_keyword_count.png"
    plt.savefig(path, dpi=300)
    print(f"Saved article keyword count plot to: {path}")


def plot_newspaper_topic_count(data, cols = 3):
    # Number of newspapers and labels
    newspapers = list(data.keys())
    labels = list(next(iter(data.values()))["scores"].keys())
    num_newspapers = len(newspapers)

    # Use a colormap with more distinct colors
    colors = plt.cm.tab20(np.linspace(0, 1, len(labels)))
    label_colors = {label: color for label, color in zip(labels, colors)}

    # Determine grid layout
    rows = (num_newspapers + cols - 1) // cols  # Calculate rows needed
    fig, axs = plt.subplots(rows, cols, figsize=(16, rows * 5), sharex=False)

    # Flatten axs to a 1D array for easy iteration
    axs = axs.flatten()

    for i, newspaper in enumerate(newspapers):
        counts = [data[newspaper]["scores"][label] for label in labels]
        x = np.arange(len(labels))
        bar_colors = [label_colors[label] for label in labels]
        axs[i].bar(x, counts, color=bar_colors, edgecolor='black')

        # Customize each subplot
        axs[i].set_title(f"{newspaper}", fontsize=14, pad=15)
        axs[i].set_ylabel("Mentions", fontsize=12)
        axs[i].set_xticks([])  # Remove x-tick labels to avoid overlap
        axs[i].grid(axis='y', linestyle='--', alpha=0.7)

        # Add the number of articles below the bar graph
        num_articles = len(data[newspaper]) - 1
        axs[i].text(0.5, -0.2, f'Articles: {num_articles}', ha='center', va='center', fontsize=12, transform=axs[i].transAxes)

    # Hide unused subplots
    for ax in axs[num_newspapers:]:
        ax.axis('off')

    # Add a legend
    handles = [plt.Line2D([0], [0], color=color, lw=4) for color in colors]
    fig.legend(handles, labels, loc='upper center', ncol=4, fontsize=12, title="Labels", bbox_to_anchor=(0.5, 0.95))

    fig.suptitle("Most mentioned topics per newspaper", fontsize=16, fontweight='bold', y=0.98)

    # Adjust spacing between subplots
    plt.subplots_adjust(hspace=0.5, wspace=0.3, top=0.85, bottom=0.1)

    # Show the plot
    plt.savefig("data/newspaper_topic_count.png", dpi=300)


def plot_submission_keyword_count(data, subreddit_name, cols=3, submissions_per_page=27):
    # Extract unique labels from the first submission
    labels = list(data[0]["labels"].keys())
    num_labels = len(labels)

    # Assign colors to labels
    colors = plt.cm.tab20(np.linspace(0, 1, num_labels))
    label_colors = {label: color for label, color in zip(labels, colors)}

    # Paginate submissions
    total_pages = (len(data) + submissions_per_page - 1) // submissions_per_page

    for page in range(total_pages):
        # Get the subset of submissions for the current page
        start_idx = page * submissions_per_page
        end_idx = min((page + 1) * submissions_per_page, len(data))
        submissions = data[start_idx:end_idx]

        # Determine grid layout
        num_submissions = len(submissions)
        rows = (num_submissions + cols - 1) // cols
        fig, axs = plt.subplots(rows, cols, figsize=(18, rows * 5), sharex=False)

        # Flatten axs for easy iteration
        axs = axs.flatten()

        for i, submission in enumerate(submissions):
            post_counts = [submission["labels"][label] for label in labels]
            comment_counts = [submission["comment_labels"].get(label, 0) for label in labels]
            x = np.arange(num_labels)

            # Plot bars for post counts (solid)
            axs[i].bar(x - 0.2, post_counts, width=0.4, label="Post Labels", color=[label_colors[label] for label in labels], edgecolor='black')

            # Plot bars for comment counts (hatch)
            axs[i].bar(x + 0.2, comment_counts, width=0.4, label="Comment Labels", 
                        color=[label_colors[label] for label in labels], edgecolor='black', hatch='//')

            # Add value labels on top of bars
            for j in range(num_labels):
                axs[i].text(x[j] - 0.2, post_counts[j] + 0.1, str(post_counts[j]), ha='center', fontsize=8)
                axs[i].text(x[j] + 0.2, comment_counts[j] + 0.1, str(comment_counts[j]), ha='center', fontsize=8)

            # Customize subplot
            axs[i].set_title(f"{submission['Title'][:50]}...", fontsize=12, pad=10)  # Reduced title padding
            axs[i].set_xticks(x)
            axs[i].set_xticklabels([])  # Hide x-tick labels
            axs[i].set_ylabel("Mentions", fontsize=10, labelpad=5)  # Reduced labelpad for y-axis
            axs[i].tick_params(axis='y', pad=3)  # Reduced padding between ticks and label
            axs[i].grid(axis="y", linestyle="--", alpha=0.7)

            # Add date and comment count below the subplot
            date = submission["Created"]
            num_comments = submission["CommCount"]
            axs[i].text(0.5, -0.1, f"Date: {date}\nComments: {num_comments}", 
                        ha='center', va='center', fontsize=10, transform=axs[i].transAxes)


        # Hide unused subplots
        for ax in axs[num_submissions:]:
            ax.axis("off")

        # Create a custom legend with Patch for the comment labels
        handles = [plt.Line2D([0], [0], color=color, lw=4) for color in label_colors.values()]
        comment_patch = [Patch(facecolor=color, edgecolor='black', hatch='//', label="Comment Labels") for color in label_colors.values()]

        # Combine the legend handles
        fig.legend(handles + comment_patch, labels + ["Comment Labels"], loc='upper center', ncol=4, fontsize=12, title="Labels", bbox_to_anchor=(0.5, 0.95))

        fig.suptitle("Submission Keyword Count Analysis", fontsize=16, fontweight='bold', y=0.98)

        # Adjust layout to decrease whitespace around the plots
        plt.subplots_adjust(hspace=0.3, wspace=0.3, top=0.88, bottom=0.12, left=0.05, right=0.95)

        # Save each page
        os.makedirs(f"reddit/{subreddit_name}", exist_ok=True)
        plt.savefig(f"reddit/{subreddit_name}/keyword_count_page_{page + 1}.png", dpi=300)
        plt.close(fig)
        
        print(f"Saved page {page + 1} of {subreddit_name}")


def plot_subreddit_keyword_count(path, normalized = False, output_dir="reddit", cols=3):
    with open(path) as r:
        data = json.load(r)

    # Extract unique labels from the first subreddit
    labels = list(next(iter(data.values()))["scores"].keys())
    num_labels = len(labels)

    # Assign colors to labels
    colors = plt.cm.tab20(np.linspace(0, 1, num_labels))
    label_colors = {label: color for label, color in zip(labels, colors)}

    # Determine grid layout
    num_subreddits = len(data)
    rows = (num_subreddits + cols - 1) // cols
    fig, axs = plt.subplots(rows, cols, figsize=(18, rows * 6), sharex=False)

    # Flatten axs for easy iteration
    axs = axs.flatten()

    for i, (subreddit, values) in enumerate(data.items()):
        scores = {label: round(value, 2) for label, value in values["scores"].items()}
        comment_scores = {label: round(value, 2) for label, value in values["comment_scores"].items()}
        x = np.arange(num_labels)

        # Plot bars for post counts (solid)
        axs[i].bar(x - 0.2, scores.values(), width=0.4, label="Post Labels", 
                    color=[label_colors[label] for label in labels], edgecolor='black')

        # Plot bars for comment counts (hatch)
        axs[i].bar(x + 0.2, comment_scores.values(), width=0.4, label="Comment Labels", 
                    color=[label_colors[label] for label in labels], edgecolor='black', hatch='//')

        # Add value labels on top of bars
        for j, label in enumerate(labels):
            axs[i].text(x[j] - 0.2, scores[label] + 0.05 * max(scores[label], 1), 
                        str(scores[label]), ha='center', fontsize=8)
            axs[i].text(x[j] + 0.2, comment_scores[label] + 0.05 * max(comment_scores[label], 1), 
                        str(comment_scores[label]), ha='center', fontsize=8)

        # Customize subplot
        axs[i].set_title(f"{subreddit} (Submissions: {values.get('num_of_sub', 'N/A')})", fontsize=10, pad=20)
        axs[i].set_xticks(x)
        axs[i].set_xticklabels([])  # Remove x-axis labels
        axs[i].set_ylabel("Mentions", fontsize=9)
        axs[i].grid(axis="y", linestyle="--", alpha=0.7)

    # Hide unused subplots
    for ax in axs[num_subreddits:]:
        ax.axis("off")

    # Create a custom legend with Patch for the comment labels
    handles = [Patch(facecolor=color, edgecolor='black', label=label) for label, color in label_colors.items()]
    comment_patch = Patch(facecolor="white", edgecolor='black', hatch='//', label="Comment Labels")

    # Combine the legend handles
    fig.legend(handles + [comment_patch], labels + ["Comment Labels"], loc='upper center', ncol=4, fontsize=10, 
                title="Labels", bbox_to_anchor=(0.5, 1.1), frameon=False)

    # Adjust the layout to increase space between the legend and the plots
    title = "Subreddit Keyword Count Analysis"
    if normalized:
        title += " (normalized)"
    fig.suptitle(title, fontsize=16, fontweight='bold', y=1.2)
    plt.subplots_adjust(hspace=0.5, wspace=0.3, top=0.8, bottom=0.2, left=0.05, right=0.95)

    # Save the figure
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{Path(path).stem}.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"Plot saved to {output_path}")



def plot_keyword_count_per_week():
    with open(r'data\article_keyword_per_week.json') as file:
        weekly_averages = json.load(file)

    data = []
    for newspaper, weeks in weekly_averages.items():
        for year_week, details in weeks.items():
            for topic, avg_count in details["averages"].items():
                data.append({
                    "Newspaper": newspaper,
                    "Week": year_week,
                    "Topic": topic,
                    "Average Count": avg_count,
                    "Article Count": details.get("article_count", 0)  # Assuming article_count is available
                })

    df = pd.DataFrame(data)

    # Convert 'Week' to a proper datetime-like format and extract week number
    df['Year'], df['WeekNum'] = zip(*df['Week'].str.split('-').apply(lambda x: (int(x[0]), int(x[1]))))
    df['WeekLabel'] = df['Year'].astype(str) + '-W' + df['WeekNum'].astype(str)

    # Create a faceted line plot using seaborn
    g = sns.FacetGrid(df, col="Newspaper", col_wrap=2, sharey=False, height=5)
    g.map_dataframe(sns.lineplot, x="WeekNum", y="Average Count", hue="Topic")

    # Adjust legend and axis labels
    g.add_legend(title="Topics")
    g.set_axis_labels("Week Number", "Average Count")
    g.set_titles("{col_name}")

    # Customize each facet's x-axis ticks
    for ax in g.axes.flatten():
        ax.set_xticks(df['WeekNum'].unique())
        ax.set_xticklabels(df['WeekLabel'].unique(), rotation=45)

        # Get the newspaper name directly from the facet grid column names
        facet_title = ax.get_title().split('=')[1].strip() if '=' in ax.get_title() else ax.get_title()

        # Track the maximum Average Count for each week
        max_avg_count_per_week = df[df['Newspaper'] == facet_title].groupby('WeekNum')['Average Count'].max()

        # Add article count text for each week at the highest Average Count
        for week_num in max_avg_count_per_week.index:
            max_avg_count = max_avg_count_per_week[week_num]
            week_data = df[(df['Newspaper'] == facet_title) & (df['WeekNum'] == week_num) & (df['Average Count'] == max_avg_count)]

            # Display article count only once for the week with the highest count
            for _, row in week_data.iterrows():
                ax.text(
                    week_num, max_avg_count + 0.3,  # Position the text just above the highest Average Count
                    f"Articles: {row['Article Count']}",
                    ha='center', va='bottom', fontsize=8
                )

    # Adjust the spacing between plots and move the legend properly
    g.fig.subplots_adjust(top=0.85, bottom=0.2, hspace=0.3)  # Increase vertical space between plots
    g.fig.legend(
        handles=g.legend.legendHandles, 
        labels=[t.get_text() for t in g.legend.texts], 
        loc='upper center', 
        ncol=3,
        bbox_to_anchor=(0.5, 1.03)  # Move the legend slightly above the plots
    )
    g.legend.remove()  # Remove duplicated legend from individual plots

    plt.tight_layout()

    output_path = "data/weekly_keyword_count.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    print(f"Plot saved to {output_path}")