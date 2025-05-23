# 🧩 League of Legends Data Pipeline

## 🌟 Features

- **Comprehensive Data Collection**

  - Summoner profiles by tier/division
  - Match histories & detailed match data
  - Frame-by-frame timeline events
  - Only collects matches within configurable time threshold (default: 12 days)
  - Implemented full exponential back-off for failed API call requests with status code 5**

- **Majority Tier Classification**

  - Majority voting system with early termination (6+ votes) for determining match game tier
  - Handles rank fluctuations between matches
  - Considers only ranked solo queue (RANKED_SOLO_5x5) matches

- **Configurable Processing**

  - Selective stage execution (enable/disable any of 4 processing stages)
  - Time-based data filtering (day_limit parameter controls maximum match age)
  - Tier-based sampling (players_per_tier and matches_per_tier parameters)

- **SQL Storage**

  - SQLite database with 5 normalized tables:
    - Summoners_Table
    - Match_ID_Table
    - Match_Data_Teams_Table
    - Match_Data_Participants_Table
    - Match_Timeline_Table
  - Batch inserts with transaction safety
  - Built-in database cleaning functionality
  - Easy CSV export capability through additional helper class

- **Production-Ready Features**
  - Rate limiting built-in (configurable calls per second)
  - Detailed logging at all processing stages
  - API key validation and management
  - Comprehensive error handling
  - Configurable batch insert sizes for memory efficiency

## 🏗️ Folder Structure

<pre>

League-of-Legends-data-pipeline/
├── data/
├── log_config/
│   ├── log_config.json
├── logs/
├── notebooks/
│   ├── playground.ipynb
├── src/
│   ├── __pycache__/
│   ├── data_collection/
│   │   ├── __ini__.py
│   │   ├── riot_api.py
│   ├── pipeline/
│   │   ├── __init__py
│   │   ├── pipeline_workflow.py
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── LoLDatabaseQuery.py
│   ├── riot_key_folder/
│   │   ├── __init__.py
│   │   ├── config_template.json
│   │   ├── riot_api_key.py
│   ├── RiotAPI_Processing_Functions.egg-info/
│   ├── __init__.py
├── .gitignore
├── photos/
│   ├── API_Call_Workflow.png
│   ├── Database_Tables_Relationships
├── documentation.txt
├── pipeline_configuration
├── main.py
├── README.md
├── setup.py
</pre>

---

## 🗃️ Database Schema

![Database Tables Relationships](photos/Database_Tables_Relationships.png)

# 🔁 API Call Workflow

![API Call Workflow](photos/API_Call_Workflow.png)

## Workflow Steps

### 1. Input Queue, Tier, Division

- **Input**: Competitive tier (e.g., Challenger, Iron), queue (e.g., ranked, normal), and division (e.g., I, II)
- **API Call**: `/lol/league/v4/entries/{queue}/{tier}/{division}`
- **Action**:
  - Retrieve summoner entries for each tier and division (ranked)
  - Store data in SQL database

### 2. Get Match IDs from puuIDs

- **Fetch**: puuID from the database
- **API Call**: `/lol/match/v5/matches/by-puuid/{puuid}/ids`
- **Action**:
  - Get the list of recent match IDs for each player
  - Store data in an SQL database

### 3. Get Match Data

- **Fetch**: matchID from the database
- **API Call**: `/lol/match/v5/matches/{matchId}`
- **Extract**:
  - Participant-level data
  - Team-level data

### 4. Get Match Timeline

- **Fetch**: matchID from the database
- **API Call**: `/lol/match/v5/matches/{matchId}/timeline`
- **Extract**:
  - Events data
  - Frame-by-frame gameplay data

## ⚙️ Features

### 🔗 Riot API Interface (`riot_api.py`)

- Interacts with Riot’s Match-V5, Summoner-V4, and Spectator-V4 endpoints
- Fetches player PUUIDs, match histories, and timelines
- Implements robust error handling and rate limit compliance

### 🧠 Pipeline Controller (`pipeline_workflow.py`)

- End-to-end orchestration of:
  - Player and match data retrieval
  - Timeline extraction
  - Filter application and database storage
- Enables batch collection and control over sample size and rank tier

### LoL Database Query Tool
A Python class for querying League of Legends match data from an SQLite database and exporting to CSV.

- Query three types of match data:
  - Participant data
  - Team data 
  - Timeline data
- Filter by game tier (e.g., "CHALLENGER", "BRONZE")
- Export results to CSV

### 🧱 Database Integration (`riot_data_database.db`)

- Lightweight SQLite database setup
- Stores structured data across:
  - Match metadata
  - Participant performance
  - Event sequences and timelines

### 🪵 Logging System (`logs/riot_data.log`)

- Tracks request success/failure and error messages
- Useful for debugging long pipeline runs
- Controlled via `configs/log_config.json`

---

## 🧪 How to Run

### Installation

To install the RiotAPI Processing Functions locally, follow these steps:

Clone the repository:

<pre>
  git clone https://github.com/PadTo/League-of-Legends-data-pipeline.git
  cd League-of-Legends-data-pipeline
</pre>

Run the following command to install the package locally:

<pre>
  pip install .
</pre>

Make sure you're in the root directory of the project (where setup.py is located) before running the install command.

### ⚙️ Configure the Pipeline

Edit the pipeline_configuration.json file located in the project root. This file contains all runtime settings required by the pipeline:

EXAMPLE:

<pre>
{
  "database_save_location": "YOUR/DESIRED/DATA/PATH",
  "logging_configuration_filepath": "YOUR/DESIRED/LOG_CONFIG_PATH/log_config.json",
  "stages_to_process": [0, 1, 0, 0], 
  "rate_limit": -1,
  "region": -1,
  "page_limit": -1,
  "event_types_to_consider": -1,
  "batch_insert_limit": 3,
  "players_per_tier": 5,
  "matches_per_tier": 100,
  "day_limit": 12,
  "clean_tables": [0, 0, 0, 0],
  "delete_summoners_table_data": 0,
  "data_save_path": "YOUR/DESIRED/DATA/PATH"
}
</pre>

⚠️ CONFIGURATION EXPLANATION:

database_save_location:

- Description: Path where processed data will be saved (e.g., a .db or .sqlite file).
- Example: "D:\\LoL Analysis Project\\data"
- Ensure the folder exists or the program has permission to create it.

logging_configuration_filepath:

- Description: Path to the logging config file (JSON format).
- Controls: What to log, log levels, format, output files, etc.
- Example: "D:\\LoL Analysis Project\\log_config\\log_config.json"

stages_to_process:

- Description: A list of 5 binary values [1, 1, 1, 1, 1] to toggle pipeline stages.
  - 1 = run the stage
  - 0 = skip the stage
- Example: [1, 0, 0, 1, 0] runs stages 1 and 4.
- Stage Description:
  - Stage 1 | Collects summoner entries by tier
  - Stage 2 | Collects match IDs by puuid
  - Stage 3 | Collects match data by match ID 
  - Stage 4 | Collects match timeline data by match ID
  - Stage 5 | Saves the data  
- Dependency rules:
  - Stage 2 depends on stage 1
  - Stage 3 depends on stage 2
  - Stage 4 depends on stage 3
  

rate_limit:

- Description: API rate limit (format: [calls, seconds]) or -1 for default/no limit.
- Example: [100, 120] = 100 requests allowed per 120 seconds.

region:

- Description: Riot API region URL to query from.
- Allowed: Only European regions (e.g., "https://eun1.api.riotgames.com")
- Invalid or unsupported regions will break the pipeline.

page_limit:

- Description: Max number of pages of match data fetched per tier/division in stage 1.
- Example: 2 = fetch up to 2 pages per bracket.
- -1 disables the limit (fetch all available pages).

event_types_to_consider:

- Description: Filters which event types to extract from match timelines.
- Example: ["CHAMPION_KILL", "BUILDING_KILL"]
- Use -1 to include all default event types.

batch_insert_limit:

- Description: Max number of entries inserted into the database at once.
- Prevents RAM issues and improves performance.
- Example: 3 = insert 3 records per batch.

players_per_tier:

- Description: Number of players to consider per tier.
- Example: 5 = fetch data for 5 players per tier.

matches_per_tier:

- Description: Number of full matches to load and process per tier.
- Can be absolute (e.g., 100) or proportional (e.g., 0.25 = 25%).
- -1 processes all available data.

day_limit:

- Description: Restricts data to matches played within the last N days.
- Example: 30 = only process matches from the last 30 days.
- -1 disables this limit and defaults to 12 days.

clean_tables Parameter:

- Description: A list of binary flags (0 or 1) that determines which database tables should have their data deleted.
- [1, 0, 0, 0]: Deletes data only from Match_ID_Table
- [0, 1, 0, 0]: Deletes data only from Match_Data_Participants_Table
- [0, 0, 1, 0]: Deletes data only from Match_Data_Teams_Table
- [0, 0, 0, 1]: Deletes data only from Match_Timeline_Table
- [1, 1, 1, 1]: Deletes data from all four tables
- Note: For Match_ID_Table, deletion is restricted to records older than the specified day_limit.

delete_summoners_table_data Parameter:

- Description: Additional safety-controlled option to delete all data from the Summoners_Table.

- Behavior:
  - 0 (default): Skips deletion of summoner data
  - 1: Prompts for confirmation before deleting (requires user to input "Y" to proceed)

data_save_path Parameter:

- Description: Saves the data to a specified location
  
### Run the Main Script

python main.py

When you run the file, you will be prompted to input your Riot API key. You can choose to replace it or skip it.

<pre>
  Do you want to replace the API key (Y for YES | N for NO)?
  If you type Y, you'll be prompted to enter your Riot API key:
</pre>

Once the key is entered, the pipeline will start and begin processing data.

# NOTE:

- The collection process takes a long time (Hours) due to rate limiting (rate limits can be adjusted based on your needs and account constraints related to rates)
- The data WILL NOT be uploaded due to the database having millions of entries
- If the pipeline's API calls have request code 400 even though the API key is valid, waiting for a moment fixes the problem
