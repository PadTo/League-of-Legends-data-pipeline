# League of Legends Data Pipeline - Comprehensive Documentation

A production-ready, scalable data pipeline for collecting, processing, and analyzing League of Legends match data using the Riot Games API. Built with Python asyncio for high-performance concurrent processing and intelligent rate limiting.

## 📋 Table of Contents

- [Overview](##overview)
- [Architecture](##architecture)
- [Features](##features)
- [Data Collection Pipeline](#data-collection-pipeline)
- [Technical Implementation](#technical-implementation)
- [Database Schema](#database-schema)
- [Rate Limiting & Error Handling](#rate-limiting--error-handling)
- [Configuration](#configuration)
- [Installation & Setup](#installation--setup)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Performance & Scalability](#performance--scalability)
- [Contributing](#contributing)

## 🎯 Overview

This data pipeline provides a solution for collecting League of Legends esports data at scale. It handles the complexities of the Riot Games API, including rate limiting, regional differences, and data transformation, while providing a clean, maintainable codebase suitable for production use.

### Key Capabilities

- **Multi-Regional Data Collection**: Supports all 12+ League of Legends regions with region grouping based on both local and continental regions
- **Comprehensive Match Analysis**: Collects detailed statistics, objectives, timeline events, and positioning data
- **Production-Grade Reliability**: Built-in error handling, exponential backoff retries, and logging
- **Scalable Architecture**: Async processing with configurable concurrency limits and token bucket rate limiting
- **Flexible Configuration**: Modular design allows selective data collection based on requirements

## 🏗️ Architecture

```
League-of-Legends-Data-Pipeline/
├── league_pipeline/              # Core pipeline package
│   ├── __init__.py
│   ├── config/                   # Configuration management
│   │   ├── __init__.py
│   │   ├── log_config.json        # Logging configuration
│   │   └── logger_config_setup.py # Logger initialization
│   ├── constants/                # Application constants and enums
│   │   ├── __init__.py
│   │   ├── database_constants.py # Database URLs, table names
│   │   ├── endpoints.py          # API endpoint definitions
│   │   ├── file_folder_paths.py  # Path management with pathlib
│   │   ├── league_ranks.py       # Tiers, divisions, queue types
│   │   ├── pipeline_constants.py # Stage configuration, processing limits
│   │   ├── rates.py              # Rate limiting parameters
│   │   └── regions.py            # Regional mappings
│   ├── db/                        # Database layer
│   │   ├── __init__.py
│   │   ├── data_saving.py         # Data persistence with conflict resolution
│   │   ├── db_connection.py       # Database queries and connections
│   │   └── models.py              # SQLAlchemy ORM models
│   ├── key/                      # API key management
│   │   ├── api_key.env           # Environment variables (gitignored)
│   │   └── key_handler.py        # Key loading and validation
│   ├── pipeline/                    # Pipeline orchestration
│   │   ├── __init__.py
│   │   └── orchestrator_pipeline.py # Main pipeline controller
│   ├── rate_limiting/            # Rate limiting implementation
│   │   ├── __init__.py
│   │   └── rate_manager.py       # Token bucket algorithm
│   ├── riot_api/               # Direct API interactions
│   │   ├── __init__.py
│   │   ├── match_data.py       # Match statistics API calls
│   │   ├── match_ids.py        # Match ID retrieval
│   │   ├── match_timeline.py   # Timeline events API
│   │   └── summoner.py         # Summoner/player data API
│   ├── services/                     # Business logic orchestration
│   │   ├── __init__.py
│   │   ├── match_data_service.py     # Match data collection service
│   │   ├── match_id_service.py       # Match ID collection service
│   │   ├── match_timeline_service.py # Timeline collection service
│   │   └── summoner_service.py       # Summoner collection service
│   └── utils/                    # Utility functions and helpers
│       ├── __init__.py
│       ├── decorators.py         # Error handling decorators
│       ├── exceptions.py         # Custom exception classes
│       ├── http_utils.py         # HTTP utilities and retry logic
│       └── time_converter.py     # Unix timestamp conversions
├── data/                          # Data storage directory
│   └── database.db                # SQLite database (created at runtime)
├── logs/                         # Application logs
│   └── pipeline.log              # Main pipeline log file
├── docs/                          # Documentation
│   └── README.md                  # Detailed documentation
├── scripts/                      # Utility scripts
│   └── run_pipeline.py           # Main execution script
├── photos/                        # Screenshots and diagrams
│   └── api_call_workflow.png
├── requirements.txt              # Python dependencies
├── setup.py                      # Package installation script
├── .gitignore                    # Git ignore rules
└── README.md                     # Main project documentation
```

### Service vs API Class Architecture

The project distinguishes between two types of classes for clean separation of concerns:

**API Classes** (`riot_api/` folder):
- **Purpose**: Direct interaction with Riot Games API endpoints
- **Functionality**: Handle single API calls and data transformation
- **Examples**: `SummonerEntries`, `MatchData`, `MatchIDsCall`, `MatchTimelineCall`
- **Responsibilities**:
  - Format API requests and handle responses
  - Transform raw API data into database-ready format
  - Handle endpoint-specific error scenarios

**Service Classes** (`services/` folder):
- **Purpose**: Orchestrate multiple API calls across regions
- **Functionality**: High-level workflow management and data collection coordination
- **Examples**: `SummonerCollectionService`, `MatchDataService`, `MatchIDCollectionService`, `MatchTimelineService`
- **Responsibilities**:
  - Manage regional processing and async task distribution
  - Coordinate data saving operations with database layer
  - Handle service-level error recovery and retry logic

This architectural separation provides:
- **Testability**: API classes can be mocked for service testing
- **Scalability**: Services can easily coordinate multiple API calls across regions
- **Reusability**: API classes can be used independently or combined in different service workflows

## 🚀 Features

### Data Collection Capabilities

- **Summoner Data**: Player profiles, rankings, tiers, divisions across all regions
- **Match Statistics**: Comprehensive KDA, gold economics, damage metrics, vision control
- **Timeline Events**: Timestamped kills, objectives, positioning data with coordinate tracking
- **Team Performance**: Win/loss records, objective control, team composition analysis

### Technical Features

- **Intelligent Rate Limiting**: Dual token bucket system (per-second and per-time-window limits)
- **Async Processing**: Concurrent API calls for optimal performance
- **Error Recovery**: Exponential backoff retries with jitter for transient failures
- **Data Integrity**: SQLite database with proper normalization and foreign key constraints
- **Flexible Time Windows**: Configurable data collection periods with Unix timestamp handling

## 📊 Data Collection Pipeline

The pipeline operates in four sequential stages, each designed to build upon the previous stage's data:

![API Call Workflow](https://raw.githubusercontent.com/PadTo/League-of-Legends-data-pipeline/main/photos/API_Call_Workflow.png)

### Stage 1: Summoner Collection


**Purpose**: Gather ranked players from competitive ladders across all regions and tiers.

**Process**:
1. Queries Riot API's ranked endpoints for each tier (Iron through Challenger)
2. Collects player PUUIDs, current ranks, and regional information
3. Maps local regions to continental regions for later token bucket limiting based on continental and local regions
4. Stores summoner profiles with date stamps for tracking

**Data Collected**:
- Player PUUID (unique identifier)
- Current competitive tier and division
- Regional assignments (local and continental)
- Collection timestamps

### Stage 2: Match ID Collection

**Purpose**: Retrieve recent match histories for collected summoners with tier validation.

**Process**:
1. Processes summoners by continental region for API efficiency
2. Queries match history with configurable time limits (default: recent matches within day limit)
3. Validates player's current tier at time of API call
4. Associates match IDs with player tier information

**Game Tier Determination**:
The system determines a player's competitive tier by making a live API call to check their current ranking at the time of match ID collection. This ensures accurate tier classification even if a player's rank has changed since the initial summoner collection. The system uses a configurable day limit (set in `constants/pipeline_constants.py`) to only collect recent matches, ensuring data relevance.

**Data Collected**:
- Match IDs with associated player PUUIDs
- Game tier classification based on current player rank
- Temporal filtering based on configured day limits

### Stage 3: Match Data Collection

**Purpose**: Collect match statistics and participant information.

**Process**:
1. Retrieves detailed match data for each collected match ID
2. Processes team-level objectives and statistics
3. Extracts individual participant performance metrics
4. Calculates derived statistics (KDA ratios, gold per minute, damage per minute)

**Data Collected**:
- Team objectives (Baron, Dragon, Tower kills)
- Individual participant statistics (KDA, gold, damage, vision)
- Champion information and role assignments
- Ping usage statistics and communication data

Note:
Match data collection process gathers data into two separate tables for teams and participants 

### Stage 4: Timeline Collection

**Purpose**: Gather timestamped events and positional data throughout matches.

**Process**:
1. Retrieves timeline data for matches with collected participant data
2. Processes event streams (kills, objectives, building destructions)
3. Extracts participant positioning data at regular intervals
4. Associates events with specific players and teams using cross-referencing

**Data Collected**:
- Timestamped kill events with coordinates
- Objective captures (Baron, Dragon, Herald)
- Player positioning data throughout matches
- Building destruction events

## 🔧 Technical Implementation

### Decorator-Based Code Reduction

The project extensively uses decorators to reduce code duplication and improve maintainability:

**`@async_api_call_error_wrapper`** (`utils/decorators.py`):
This decorator handles all API call error scenarios, significantly reducing boilerplate code across API classes:

- **Automatic Retry Logic**: Handles server errors (5xx) with exponential backoff
- **Rate Limit Management**: Processes 429 errors with appropriate wait times
- **Error Classification**: Distinguishes between retryable and non-retryable errors
- **Logging Integration**: Provides consistent error logging across all API calls

Without this decorator, each API method would need 20-30 lines of error handling code. With it, methods focus purely on their business logic.

### Unix Time Converter Utility

**`unix_time_converter`** (`utils/time_converter.py`):
Provides flexible time unit conversions for API timestamp handling:

```python
# Convert days to seconds for API time filtering
day_limit_seconds = unix_time_converter(7, "d", "s")  # 7 days to seconds
# Convert API milliseconds to readable seconds
readable_time = unix_time_converter(1640995200000, "mili", "s")
```

Supports conversions between: milliseconds, seconds, minutes, hours, and days.

### HTTP Utilities and Retry Logic

**`http_utils.py`** provides sophisticated HTTP request handling:

**`safely_fetch_rate_limited_data`**:
- Integrates with token bucket rate limiter
- Ensures requests comply with API limits before execution
- Handles response validation and JSON parsing

**`exponential_back_off`**:
- Implements exponential backoff with configurable base values
- Includes jitter to prevent thundering herd problems
- Caps maximum wait times to prevent excessive delays

**`retry_api_call`**:
- Determines retry eligibility based on error type and attempt count
- Provides detailed logging for retry decisions

### Token Bucket Rate Limiting

**Dual Bucket System** (`rate_limiting/rate_manager.py`):

The implementation uses separate "fast" and "slow" token buckets for each region:

- **Fast Bucket**: Per-second rate limits (e.g., 20 requests/second)
- **Slow Bucket**: Per-time-window limits (e.g., 100 requests/120 seconds)

**Key Features**:
- Independent rate limiting per region
- Automatic token refill based on elapsed time
- Request blocking until tokens are available
- Sleep time calculation for optimal waiting

## 🗄️ Database Schema

The database uses SQLAlchemy ORM with SQLite, designed for optimal data relationships and query performance:

### Core Tables

**Summoners Table**:
- Primary Key: `puuid` (Player UUID)
- Regional information (local and continental)
- Current competitive tier and division
- Collection timestamps

**MatchIDs Table**:
- Primary Key: `match_id`
- Foreign Key: `puuid` → Summoners
- Game tier classification
- Bridge table connecting players to matches

**MatchDataTeams Table**:
- Composite Key: `(match_id, team_id)`
- Team-level objectives and performance
- Win/loss results and game ending conditions

**MatchDataParticipants Table**:
- Composite Key: `(puuid, match_id)`
- Comprehensive individual player statistics
- KDA, economy, vision, and communication metrics

**MatchTimeline Table**:
- Composite Key: `(match_id, puuid, timestamp)`
- Timestamped events and positioning data
- Event classification and coordinate tracking

### Database Features

- **Foreign Key Constraints**: Ensures data integrity and referential consistency
- **Composite Primary Keys**: Optimal for time-series and multi-dimensional data
- **Conflict Resolution**: INSERT OR IGNORE for batch operations, IntegrityError handling for singles
- **Scalable Design**: Normalized structure supports millions of records efficiently

## ⚡ Rate Limiting & Error Handling

### Rate Limiting Strategy

**Token Bucket Algorithm**:
The system implements a sophisticated dual token bucket rate limiter that respects both per-second and per-time-window API limits:

```python
# Example rate limits (configurable in constants/rates.py)
MAX_CALLS_PER_SECOND = 20     # Fast bucket
MAX_CALLS = 100               # Slow bucket capacity
WINDOW = 120                  # Slow bucket window (seconds)
```

**Regional Independence**:
Each region maintains separate token buckets, allowing parallel processing across regions while respecting per-region limits.

### Error Handling Strategy

**Exponential Backoff with Jitter**:
- Base value: Configurable starting delay
- Maximum wait time: Capped to prevent excessive delays
- Jitter: Random factor prevents thundering herd problems

**Error Classification**:
- **Retryable Errors**: Server errors (5xx), timeouts, incomplete reads
- **Non-Retryable Errors**: Client errors (4xx), authentication failures
- **Rate Limit Errors**: Special handling with fixed wait times

## ⚙️ Configuration

The system uses a comprehensive constants-based configuration system:

### Database Constants (`constants/database_constants.py`)
- Database name and SQLAlchemy URL patterns
- Table naming conventions
- Connection parameters

### API Endpoints (`constants/endpoints.py`)
- Base URLs for different API regions
- Endpoint patterns for all API calls
- Parameter formatting templates

### File Paths (`constants/file_folder_paths.py`)
- Flexible path management using `pathlib`
- Relative path construction with `__file__.parent.parent`
- Configurable data and key storage locations

### League Ranks (`constants/league_ranks.py`)
- Competitive tiers (Iron through Challenger)
- Divisions (I, II, III, IV)
- Queue types and match classifications

### Pipeline Configuration (`constants/pipeline_constants.py`)
- **Stages to Process**: Binary flags for each pipeline stage
- **Data Processing Config**:
  - `PAGE_LIMIT`: Number of result pages for summoner entries
  - `START` and `COUNT`: Pagination parameters for match ID API calls
  - `DAY_LIMIT`: Time window for match collection (e.g., last 7 days)

### Rate Limiting (`constants/rates.py`)
- Token bucket parameters (capacity, refill rates)
- Retry limits and backoff parameters
- Sleep times for rate limit exceeded scenarios

### Regional Configuration (`constants/regions.py`)
- Local regions (NA1, EUW1, KR, etc.)
- Continental regions (AMERICAS, EUROPE, ASIA)
- Region mapping between local and continental

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Riot Games Developer API Key ([Get one free](https://developer.riotgames.com))
- ~2GB free disk space for database storage

### Installation Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/League-of-Legends-Data-Pipeline.git
   cd League-of-Legends-Data-Pipeline
   ```

2. **Create Virtual Environment** (Recommended):
   ```bash
   python -m venv league_pipeline_env
   source league_pipeline_env/bin/activate  # On Windows: league_pipeline_env\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Environment**:
   ```bash
   # Copy environment template
   cp .env.example league_pipeline/key/api_key.env
   
   # Edit with your API key
   echo "RIOT_API_KEY=RGAPI-your-api-key-here" > league_pipeline/key/api_key.env
   ```

5. **Initialize Database**:
   ```bash
   python scripts/setup_database.py
   ```

6. **Validate Setup**:
   ```bash
   python scripts/validate_setup.py
   ```

### Quick Start Scripts

The project includes convenient scripts for common operations:

- **`scripts/run_pipeline.py`**: Execute the complete data collection pipeline
- **`scripts/setup_database.py`**: Initialize database tables and structure
- **`scripts/validate_setup.py`**: Verify API key and system requirements

## 🚀 Usage Examples

### Quick Start - Complete Pipeline

```bash
# Using the provided script
python scripts/run_pipeline.py

# Or programmatically
python -c "
from league_pipeline.pipeline.orchestrator_pipeline import PipelineOrchestrator
orchestrator = PipelineOrchestrator()
orchestrator.run_full_pipeline()
"
```


### Configuration Examples

#### Pipeline Stage Configuration
```python
# In constants/pipeline_constants.py

class Stages:
    # Set to True to enable, False to disable each stage
    TO_PROCESS = [
        True,  # Stage 1: Summoner Collection
        True,  # Stage 2: Match ID Collection  
        False,  # Stage 3: Match Data Collection (disabled)
        False   # Stage 4: Timeline Collection (disabled)
    ]

class DataProcessingConfig:
    PAGE_LIMIT = 10        # Pages per tier/region for summoner collection
    START = 0              # Starting index for match ID pagination
    COUNT = 100            # Number of matches per request
    DAY_LIMIT = 7          # Only collect matches from last N days
```

#### Rate Limiting Configuration
```python
# In constants/rates.py

class Rates:
    MAX_CALLS_PER_SECOND = 20    # Fast bucket capacity
    MAX_CALLS = 100              # Slow bucket capacity  
    WINDOW = 120                 # Slow bucket time window (seconds)
    MAX_API_CALL_RETRIES = 3     # Retry attempts for failed calls
    EXPONENTIAL_BACK_OFF_BASE_VALUE = 2.0  # Base for exponential backoff
```

## 📈 Performance & Scalability

### Performance Characteristics

- **Concurrent Processing**: Async processing with configurable semaphores
- **Memory Efficient**: Streaming data processing, minimal memory footprint
- **Database Optimized**: Batch inserts with conflict resolution
- **Rate Limit Compliant**: Intelligent token bucket prevents API violations

### Scalability Considerations

- **Regional Parallelization**: Independent processing per region
- **Configurable Concurrency**: Adjustable semaphore limits based on system resources
- **Database Scaling**: SQLite suitable for single-machine deployments up to millions of records
- **API Efficiency**: Optimized endpoint usage minimizes API call requirements

### Monitoring and Logging

- **Comprehensive Logging**: Detailed logs for debugging and monitoring
- **Rate Limit Tracking**: Token bucket status logging
- **Error Classification**: Detailed error reporting and classification
- **Performance Metrics**: Processing time and throughput logging

## 🤝 Contributing

I welcome contributions to improve the pipeline's capabilities and performance.

**💡 Have questions?** Check the documentation or open a discussion thread.
