# Standalone AIOS Implementation

This project is a standalone implementation of the AI Operating System (AIOS) concept as described by Liam Ottley in his webinar and landing page. It is designed to be a clean, self-contained system that is not dependent on any pre-existing codebase like Aquadex-OS.

## Architecture

The system is built around a 5-layer architecture:

1.  **Context OS:** A set of Markdown files that provide the AI with a deep, living understanding of the business.
2.  **Data OS:** A local SQLite database and a suite of data collectors that create a single source of truth for all business metrics.
3.  **Intelligence Layer:** An analytical engine that processes unstructured data (meetings, Slack messages, voice notes) to extract actionable insights.
4.  **Automation Layer:** A series of cron jobs and execution scripts that automate key business processes.
5.  **Output/Interface Layer:** The primary interface for interacting with the system, a Telegram bot, which also delivers key outputs like the daily brief.

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone <this-repo-url>
    cd liam_ottley_aios
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    -   Copy the `.env.example` file to `.env`.
    -   Fill in all the required API keys and configuration variables.

4.  **Initialize the Database:**
    ```bash
    python3 execution/data_os/db_setup.py
    ```

5.  **Run an Initial Data Snapshot:**
    ```bash
    python3 execution/data_os/snapshot.py
    ```

6.  **Set Up Cron Jobs:**
    -   Edit the cron job scripts in the `cron/` directory to use the correct absolute paths for your system.
    -   Add them to your system's crontab. For example:
        ```crontab
        # Daily data snapshot at 6 AM
        0 6 * * * /path/to/your/project/liam_ottley_aios/cron/data_snapshot.sh >> /path/to/your/project/liam_ottley_aios/logs/cron.log 2>&1

        # Daily brief at 7 AM
        0 7 * * * /path/to/your/project/liam_ottley_aios/cron/daily_brief.sh >> /path/to/your/project/liam_ottley_aios/logs/cron.log 2>&1
        ```

7.  **Start the Telegram Bot:**
    ```bash
    python3 execution/telegram/bot.py
    ```

## How to Use

Once the bot is running, you can interact with your AIOS through the Telegram interface:

-   **Send a text message:** Any text message will be treated as a new task and processed by the GTD system.
-   **Send a voice note:** Your voice note will be transcribed and analyzed for tasks and insights.
-   **Use slash commands:**
    -   `/brief`: Manually trigger the generation of the daily brief.
    -   `/query <your question>`: Ask a natural language question about your business data (e.g., `/query what was our MRR last month?`).
