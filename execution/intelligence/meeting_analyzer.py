#!/usr/bin/env python3
"""
Intelligence Layer: Meeting Analyzer

This script uses an LLM to analyze meeting transcripts for tasks, strategy changes,
and other key insights.
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

def analyze_transcript(transcript_text):
    """Analyzes a single transcript using an LLM."""
    business_context = load_context()

    prompt = f"""You are the AI Operating System for a multi-faceted business.
Your task is to analyze the following meeting transcript and extract key insights.

**Business Context:**
{business_context}

**Meeting Transcript:**
{transcript_text}

**Analysis:**
Based on the transcript and the business context, extract the following information in JSON format:

-   `summary`: A concise, one-paragraph summary of the meeting.
-   `action_items`: A list of specific, actionable tasks. For each task, include:
    -   `task`: The description of the task.
    -   `owner`: The person responsible for the task (use names from the team roster).
    -   `due_date`: The suggested due date, if mentioned.
-   `strategy_flags`: Any discussions that indicate a potential change or addition to the company strategy.
-   `content_ideas`: Any ideas mentioned that could be turned into content (YouTube videos, blog posts, etc.).
-   `sentiment`: The overall sentiment of the meeting (e.g., Positive, Neutral, Negative, Mixed).

**JSON Output:**
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides analysis in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        analysis_json = response.choices[0].message["content"]
        return json.loads(analysis_json)

    except Exception as e:
        print(f"An error occurred during transcript analysis: {e}")
        return None

if __name__ == "__main__":
    # Example usage with a dummy transcript
    dummy_transcript = """
    Liam: Okay team, great meeting. So, just to recap, we need to launch the new AaaS offering by the end of Q1.
    Sarah (assumed): I can take the lead on drafting the sales page copy.
    Liam: Perfect. And let's also brainstorm a YouTube video to announce it. Maybe something about the future of AI in business.
    """
    analysis = analyze_transcript(dummy_transcript)
    if analysis:
        print(json.dumps(analysis, indent=2))
