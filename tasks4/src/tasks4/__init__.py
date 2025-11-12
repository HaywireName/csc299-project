from openai import OpenAI

def main():
    """Main function that processes task descriptions and prints summaries."""
    # Initialize OpenAI client (reads OPENAI_API_KEY from environment)
    client = OpenAI()

    # Sample paragraph-length task descriptions
    tasks = [
        "I need to prepare a comprehensive presentation for the quarterly review meeting scheduled for next Tuesday at 2 PM. This involves gathering all the sales data from Q3, creating clear visualizations showing trends and comparisons to previous quarters, writing detailed speaker notes for each slide to ensure I don't miss key points, and rehearsing the delivery at least twice to feel confident. The whole thing should take about 6 hours total of focused work.",
        
        "My kitchen faucet has been dripping constantly for the past week and it's getting annoying plus wasting water. I need to either fix it myself by watching some YouTube tutorials and replacing the washer, or call a professional plumber if it turns out to be more complicated than I can handle. Before doing anything, I should also check if this kind of repair is covered under my home warranty to avoid unnecessary expenses."
    ]

    # Loop through each task and get a summary
    print("Task Summaries:\n")
    for i, task in enumerate(tasks, 1):
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{
                "role": "user",
                "content": f"Summarize this task as a short phrase (5 words or less): {task}"
            }]
        )
        summary = response.choices[0].message.content
        print(f"{i}. {summary}")

if __name__ == "__main__":
    main()