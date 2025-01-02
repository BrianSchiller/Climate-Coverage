import matplotlib.pyplot as plt
import numpy as np

def plot_article_keyword_count(data, cols = 3):
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
    fig.legend(handles, labels, loc='upper center', ncol=4, fontsize=12, title="Labels")

    # Adjust spacing between subplots
    plt.subplots_adjust(hspace=0.5, wspace=0.3, top=0.85, bottom=0.1)

    # Add shared labels
    fig.text(0.5, 0.04, "Labels", ha='center', fontsize=14)
    fig.text(0.04, 0.5, "Mentions", va='center', rotation='vertical', fontsize=14)

    # Show the plot
    plt.savefig("data/article_keyword_count.png", dpi=300)