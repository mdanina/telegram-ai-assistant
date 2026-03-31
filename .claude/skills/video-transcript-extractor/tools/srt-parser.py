#!/usr/bin/env python3
"""
SRT Subtitle Parser for Video Transcript Extraction

Parses SRT (SubRip) subtitle files into clean text format with timestamps.
Can be used as standalone script or imported as module.

Usage:
    python srt-parser.py input.srt [output.txt]

    If output file not specified, prints to stdout.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional


class SubtitleEntry:
    """Represents a single subtitle entry."""

    def __init__(self, index: int, start_time: str, end_time: str, text: str):
        self.index = index
        self.start_time = start_time
        self.end_time = end_time
        self.text = text

    def to_timestamp_format(self) -> str:
        """Convert to [MM:SS] timestamp format."""
        # Convert HH:MM:SS,mmm to MM:SS
        time_parts = self.start_time.split(':')
        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        seconds = time_parts[2].split(',')[0]

        total_minutes = hours * 60 + minutes
        return f"[{total_minutes}:{seconds}]"

    def __str__(self) -> str:
        return f"{self.to_timestamp_format()} {self.text}"


class SRTParser:
    """Parser for SRT subtitle files."""

    @staticmethod
    def parse_file(filepath: str) -> List[SubtitleEntry]:
        """
        Parse an SRT file and return list of subtitle entries.

        Args:
            filepath: Path to SRT file

        Returns:
            List of SubtitleEntry objects
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        return SRTParser.parse_content(content)

    @staticmethod
    def parse_content(content: str) -> List[SubtitleEntry]:
        """
        Parse SRT content string.

        SRT format:
        1
        00:00:00,000 --> 00:00:02,000
        Subtitle text here

        2
        00:00:02,000 --> 00:00:04,000
        Next subtitle
        """
        entries = []

        # Split by double newline to get individual entries
        blocks = re.split(r'\n\s*\n', content.strip())

        for block in blocks:
            lines = block.strip().split('\n')

            if len(lines) < 3:
                continue

            # First line: index
            try:
                index = int(lines[0].strip())
            except ValueError:
                continue

            # Second line: timestamps
            timestamp_match = re.match(
                r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})',
                lines[1]
            )

            if not timestamp_match:
                continue

            start_time = timestamp_match.group(1)
            end_time = timestamp_match.group(2)

            # Remaining lines: subtitle text
            text = ' '.join(lines[2:])

            entries.append(SubtitleEntry(index, start_time, end_time, text))

        return entries

    @staticmethod
    def to_transcript(entries: List[SubtitleEntry],
                     include_timestamps: bool = True,
                     merge_consecutive: bool = True) -> str:
        """
        Convert subtitle entries to clean transcript format.

        Args:
            entries: List of SubtitleEntry objects
            include_timestamps: Whether to include [MM:SS] timestamps
            merge_consecutive: Merge consecutive entries with same speaker

        Returns:
            Formatted transcript string
        """
        if not entries:
            return ""

        lines = []
        current_text = []
        last_timestamp = None

        for entry in entries:
            timestamp = entry.to_timestamp_format()

            if merge_consecutive:
                # If this is continuation of previous line, append
                if current_text and not entry.text.endswith('.') and not entry.text.endswith('!') and not entry.text.endswith('?'):
                    current_text.append(entry.text)
                else:
                    # Flush current text
                    if current_text:
                        text = ' '.join(current_text)
                        if include_timestamps:
                            lines.append(f"{last_timestamp} {text}")
                        else:
                            lines.append(text)

                    # Start new text
                    current_text = [entry.text]
                    last_timestamp = timestamp
            else:
                if include_timestamps:
                    lines.append(f"{timestamp} {entry.text}")
                else:
                    lines.append(entry.text)

        # Flush remaining text
        if merge_consecutive and current_text:
            text = ' '.join(current_text)
            if include_timestamps:
                lines.append(f"{last_timestamp} {text}")
            else:
                lines.append(text)

        return '\n'.join(lines)


def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("Usage: python srt-parser.py input.srt [output.txt]")
        print("\nOptions:")
        print("  --no-timestamps    Don't include timestamps in output")
        print("  --no-merge        Don't merge consecutive lines")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None

    # Parse options
    include_timestamps = '--no-timestamps' not in sys.argv
    merge_consecutive = '--no-merge' not in sys.argv

    # Check input file exists
    if not Path(input_file).exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    # Parse SRT file
    try:
        entries = SRTParser.parse_file(input_file)
        transcript = SRTParser.to_transcript(
            entries,
            include_timestamps=include_timestamps,
            merge_consecutive=merge_consecutive
        )

        # Output
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(transcript)
            print(f"Transcript written to: {output_file}")
            print(f"Entries processed: {len(entries)}")
        else:
            print(transcript)

    except Exception as e:
        print(f"Error parsing SRT file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
