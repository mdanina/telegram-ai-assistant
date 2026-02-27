#!/usr/bin/env python3
"""
Intelligence Layer: Fireflies.ai Client

This script fetches recent meeting transcripts from the Fireflies.ai API.
"""

import os
import requests
from datetime import datetime, timedelta

API_KEY = os.getenv("FIREFLIES_API_KEY")
GRAPHQL_ENDPOINT = "https://api.fireflies.ai/graphql"

def get_recent_transcripts():
    """Fetches transcripts from the last 24 hours."""
    if not API_KEY:
        print("FIREFLIES_API_KEY not set. Skipping Fireflies transcript fetching.")
        return []

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Get transcripts from the last day
    query = """
        query GetRecentTranscripts($from: Float!) {
            transcripts(from: $from) {
                id
                title
                transcript_url
                date
                sentences {
                    text
                    speaker_name
                }
            }
        }
    """

    yesterday_timestamp = (datetime.now() - timedelta(days=1)).timestamp()

    variables = {
        "from": yesterday_timestamp
    }

    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            headers=headers,
            json={"query": query, "variables": variables}
        )
        response.raise_for_status()
        data = response.json()
        
        if 'errors' in data:
            print(f"GraphQL Errors: {data['errors']}")
            return []

        return data.get("data", {}).get("transcripts", [])

    except requests.exceptions.RequestException as e:
        print(f"Error fetching transcripts from Fireflies: {e}")
        return []

if __name__ == "__main__":
    transcripts = get_recent_transcripts()
    if transcripts:
        print(f"Successfully fetched {len(transcripts)} transcripts.")
        for transcript in transcripts:
            print(f"- {transcript['title']}")
    else:
        print("No recent transcripts found.")
