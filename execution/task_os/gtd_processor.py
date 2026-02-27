#!/usr/bin/env python3
"""
Task OS: GTD Processor

This script takes a raw task (from Telegram, voice, etc.) and processes it
using the GTD methodology, then creates it in the appropriate project management tool.
"""

import os
import openai
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

def load_context():
    """Loads the core business context from the context/ directory."""
    context = ""
    context_dir = os.path.join(os.path.dirname(__file__), "..", "..", "context")
    for filename in os.listdir(context_dir):
        if filename.endswith(".md"):
            with open(os.path.join(context_dir, filename), "r") as f:
                context += f"\n\n--- {filename} ---\n\n" + f.read()
    return context

def process_raw_task(raw_task_text):
    """Processes a raw task using an LLM to apply the GTD framework."""
    business_context = load_context()

    prompt = f"""You are the GTD (Getting Things Done) processor for an AI Operating System.
Your job is to take a raw, unstructured task and clarify it into a structured format.

**Business Context:**
{business_context}

**Raw Task:**
{raw_task_text}

**GTD Processing:**
Analyze the raw task and determine the following, providing your output in JSON format:

-   `next_action`: What is the very next physical action required to move this forward?
-   `project`: If this is part of a larger outcome (a "project"), what is the name of that project?
-   `context`: Where does this action need to be done (e.g., @computer, @phone, @office)?
-   `delegated_to`: If this task should be delegated, who is the appropriate person (use the team roster)?
-   `due_date`: If a due date is mentioned or implied, what is it?
-   `is_someday_maybe`: Is this a task that doesn't need to be done now, but might be in the future?

**JSON Output:**
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful GTD assistant that provides analysis in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        processed_task_json = response.choices[0].message["content"]
        processed_task = json.loads(processed_task_json)

        # In a real system, you would now use an API (e.g., Notion, ClickUp, Asana)
        # to create this task in your project management tool.
        print("--- Processed Task ---")
        print(json.dumps(processed_task, indent=2))
        print("\n(Task would now be created in your PM tool)")

        return processed_task

    except Exception as e:
        print(f"An error occurred during GTD processing: {e}")
        return None

if __name__ == "__main__":
    example_task = "remind me to follow up with the new lead from the webinar next Tuesday"
    process_raw_task(example_task)
