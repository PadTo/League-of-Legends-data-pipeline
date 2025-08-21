# League of Legends Data Pipeline - Comprehensive Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Database Schema](#database-schema)
6. [Pipeline Stages](#pipeline-stages)
7. [API Integration](#api-integration)
8. [Rate Limiting](#rate-limiting)
9. [Usage Examples](#usage-examples)
10. [Monitoring & Logging](#monitoring--logging)
11. [Performance Optimization](#performance-optimization)
12. [Troubleshooting](#troubleshooting)
13. [Contributing](#contributing)
14. [Advanced Topics](#advanced-topics)

## Overview

This project implements a production-ready data pipeline for collecting, processing, and storing League of Legends match data from the Riot Games API. It's designed to handle large-scale data collection with proper rate limiting, error handling, and concurrent processing.

### Key Features

- **Scalable Architecture**: Modular design supports easy extension and maintenance
- **Multi-Region Support**: Collect data from all 14 League of Legends regions
- **Intelligent Rate Limiting**: Custom token bucket algorithm respects API limits
- **Async Processing**: Concurrent API calls with proper resource management
- **Comprehensive Error Handling**: Exponential backoff, retries, and graceful degradation
- **Production Logging**: Detailed logging with configurable levels and rotation

## Architecture

### Project Structure

```
league_pipeline/
├── config/                 # Configuration files
├── constants/              # Enums and constants
├── db/                    # Database models and connections
├── key/                   # API key management
├── pipeline/              # Main pipeline orchestration
├── rate_limiting/         # Token bucket rate limiting
├── riot_api/              # API client implementations
├── services/              # Business logic services
└── utils/                 # Utility functions
```

### Component Overview

#### Services Layer
- **SummonerCollectionService**: Collects player ranking data
- **MatchIDCollectionService**: Gathers match identifiers
- **MatchDataService**: Retrieves detailed match statistics
- **MatchTimelineService**: Collects positional and event timeline data

#### API Layer
- **SummonerEntries**: Player ranking and tier information
- **MatchIDsCall**: Match ID collection with filtering
- **MatchData**: Comprehensive match statistics
- **MatchTimelineCall**: Timeline events and positioning

#### Database Layer
- **Models**: SQLAlchemy ORM models for all data types
- **DataSaver**: Batch insertion with conflict resolution
- **DatabaseQuery**: Complex queries for data relationships

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Riot Games API key (free registration at [developer.riotgames.com](https://developer.riotgames.com))
- 1-2GB available disk space for database storage

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/league-of-legends-data-pipeline.git
   cd league-of-legends-data-pipeline
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv league_pipeline_env
   source league_pipeline_env/bin/activate  # Linux/Mac
   # or
   league_pipeline_env\Scripts\activate     # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up API Key**
   ```bash
   # Create the key file
   mkdir -p league_pipeline/key
   echo "RIOT_API_KEY=RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" > league_pipeline/key/api_key.env
   ```

5. **Initialize Database**
   ```bash
   python -c "from league_pipeline.db.models import DataBase; DataBase('data').create_all_tables()"
   ```

## Configuration

### Pipeline Configuration

The pipeline behavior is controlled through several configuration files:

#### `league_pipeline/constants/pipeline_constants.py`

```python
class DataProcessingConfig:
    PAGE_LIMIT = 2              # Pages per API call
    DAY_LIMIT = 10              # Days of match history
    MATCHES_PER_TIER = 50       # Matches to collect per tier
    PLAYERS_PER_TIER = 100      # Players to collect per tier
    START = 0                   # Starting index for pagination
    COUNT = 100                 # Items per API call
```

#### Rate Limiting Configuration

```python
class Rates(Enum):
    MAX_CALLS = 100                    # Calls per 2-minute window
    WINDOW = 120                       # Window in seconds
    MAX_CALLS_PER_SECOND = 20          # Calls per second
    MAX_API_CALL_RETRIES = 30          # Maximum retry attempts
    MAX_WAITING_TIME_BETWEEN_RETRIES = 120  # Max backoff time
```

### Logging Configuration

Logging is configured via `league_pipeline/config/log_config.json`:

```json
{
  "version": 1,
  "disable_existing_loggers": false,
  "formatters": {
    "detailed": {
      "format": "[%(levelname)s|%(module)s|%(lineno)d|%(asctime)s: %(message)s]",
      "datefmt": "%Y-%m-%dT%H:%M:%S%z"
    }
  },
  "handlers": {
    "file": {
      "class": "logging.handlers.RotatingFileHandler",
      "level": "DEBUG",
      "filename": "logs/pipeline.log",
      "maxBytes": 10000000,
      "backupCount": 2
    }
  }
}
```

## Database Schema

### Core Tables

#### Summoners Table
Stores player information and rankings:
```sql
CREATE TABLE "Summoners" (
    puuId TEXT PRIMARY KEY,
    continentalRegion TEXT,
    localRegion TEXT,
    currentTier TEXT,
    currentDivision TEXT,
    dateCollected TEXT
);
```

#### Match IDs Table
Contains match identifiers and metadata:
```sql
CREATE TABLE "Match IDs" (
    matchId TEXT PRIMARY KEY,
    puuId TEXT,
    gameTier TEXT,
    FOREIGN KEY(puuId) REFERENCES Summoners(puuId)
);
```

#### Match Data (Participants) Table
Detailed player performance statistics:
```sql
CREATE TABLE "Match Data (Participants)" (
    puuId TEXT,
    matchId TEXT,
    teamId INTEGER,
    championKills INTEGER,
    assists INTEGER,
    deaths INTEGER,
    KDA REAL,
    goldEarned INTEGER,
    goldPerMinute REAL,
    -- ... additional 25+ performance metrics
    PRIMARY KEY (puuId, matchId)
);
```

#### Match Timeline Table
Positional and event data over time:
```sql
CREATE TABLE "Match Timeline" (
    matchId TEXT,
    puuId TEXT,
    timestamp INTEGER,
    teamId TEXT,
    x INTEGER,
    y INTEGER,
    event TEXT,
    type TEXT,
    PRIMARY KEY (matchId, puuId, timestamp)
);
```

### Relationships

- **Summoners** ↔ **Match IDs**: One-to-many (players can have multiple matches)
- **Match IDs** ↔ **Match Data**: One-to-many (matches have multiple participants)
- **Match Data** ↔ **Match Timeline**: One-to-many (participants have multiple timeline events)

## Pipeline Stages

The pipeline processes data in four sequential stages:

### Stage 1: Summoner Collection
- **Purpose**: Gather player information from ranked leaderboards
- **Data Source**: League-v4 API endpoints
- **Output**: Player PUUIDs, ranks, regions, tiers
- **Regions**: All 14 game regions (NA1, EUW1, KR, etc.)

### Stage 2: Match ID Collection
- **Purpose**: Collect match identifiers for each player
- **Data Source**: Match-v5 by-puuid endpoints
- **Filtering**: Recent matches (configurable day limit)
- **Output**: Match IDs linked to players and tiers

### Stage 3: Match Data Collection
- **Purpose**: Retrieve detailed match statistics
- **Data Source**: Match-v5 by-matchId endpoints
- **Metrics**: 30+ performance indicators per player
- **Output**: Comprehensive match and player statistics

### Stage 4: Timeline Collection
- **Purpose**: Gather positional and event timeline data
- **Data Source**: Match-v5 timeline endpoints
- **Events**: Kills, objectives, positioning over time
- **Output**: Time-series data for advanced analysis

## API Integration

### Riot Games API Coverage

The pipeline integrates with multiple Riot API endpoints:

#### Account-v1
- `/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}`
- `/riot/account/v1/accounts/by-puuid/{puuId}`

#### League-v4
- `/lol/league/v4/challengerleagues/by-queue/{queue}`
- `/lol/league/v4/grandmasterleagues/by-queue/{queue}`
- `/lol/league/v4/masterleagues/by-queue/{queue}`
- `/lol/league-exp/v4/entries/{queue}/{tier}/{division}`

#### Match-v5
- `/lol/match/v5/matches/by-puuid/{puuId}/ids`
- `/lol/match/v5/matches/{matchId}`
- `/lol/match/v5/matches/{matchId}/timeline`

### Regional Routing

The pipeline automatically handles regional routing:

- **Platform Regions**: BR1, EUN1, EUW1, JP1, KR, LA1, LA2, ME1, NA1, OC1, SG2, TR1, TW2, VN2
- **Continental Routing**: AMERICAS, ASIA, EUROPE
- **Auto-mapping**: Platform regions automatically route to correct continental endpoints

## Rate Limiting

### Token Bucket Algorithm

The pipeline implements a sophisticated dual-token bucket system:

#### Bucket Configuration
- **Slow Bucket**: 100 calls per 120 seconds
- **Fast Bucket**: 20 calls per 1 second
- **Regional Isolation**: Separate buckets per region

#### Implementation Details

```python
class TokenBucket:
    def __init__(self, regions: Type[Enum], logger: Logger):
        # Initialize separate buckets for each region
        for region in regions:
            self.token_bucket_regions[region] = {
                "slow_bucket_capacity": 100,
                "slow_bucket_rate": 100/120,
                "fast_bucket_capacity": 20,
                "fast_bucket_rate": 20.0
            }
    
    def allow_request(self, region: str) -> bool:
        # Check both buckets before allowing request
        return (self.slow_tokens > 0 and self.fast_tokens > 0)
```

### Adaptive Backoff

When rate limits are exceeded:
1. **Exponential Backoff**: `sleep_time = base^attempt`
2. **Jitter Addition**: Randomization prevents thundering herd
3. **Maximum Backoff**: Capped at 120 seconds
4. **Smart Retry**: Different strategies for different error types

## Usage Examples

### Basic Pipeline Execution

```python
from league_pipeline.pipeline.main_pipeline import RiotPipeline

# Initialize pipeline
pipeline = RiotPipeline(
    db_save_location="./data",
    api_key="RGAPI-your-key-here",
    stages_to_process=[1, 1, 1, 1],  # All stages
    players_per_tier=100,
    matches_per_tier=50
)

# Start data collection
pipeline.start_pipeline()
```

### Custom Configuration

```python
# Custom rate limiting
custom_rates = {
    'max_calls': 50,
    'window': 60,
    'max_calls_per_second': 10
}

# Region-specific collection
regions = ['NA1', 'EUW1', 'KR']

# Tier filtering
tiers = ['CHALLENGER', 'GRANDMASTER', 'MASTER']

pipeline = RiotPipeline(
    regions=regions,
    tiers=tiers,
    rate_limits=custom_rates
)
```

### Service-Level Usage

```python
import asyncio
from league_pipeline.services.summoner_service import SummonerCollectionService

# Initialize service
service = SummonerCollectionService(
    db_location="./data",
    database_name="league_data",
    regions=Region,
    queue="RANKED_SOLO_5x5",
    api_key="your-key"
)

# Collect summoner data
asyncio.run(service.async_get_and_save_summoner_entries())
```

## Monitoring & Logging

### Log Levels and Categories

#### DEBUG Level
- Token bucket state changes
- Individual API call details
- Database transaction details

#### INFO Level
- Pipeline stage transitions
- Successful API responses
- Data collection summaries

#### WARNING Level
- Rate limit approaches
- Retry attempts
- Data quality issues

#### ERROR Level
- API failures
- Database errors
- Pipeline failures

### Log File Organization

```
logs/
├── pipeline.log           # Main application log
├── pipeline.log.1         # Rotated log (previous)
├── pipeline.log.2         # Rotated log (older)
└── error_summary.log      # Error-only aggregation
```

### Performance Metrics

The pipeline automatically tracks:
- **API Call Success Rate**: Percentage of successful calls
- **Average Response Time**: Per endpoint timing
- **Rate Limit Utilization**: Token bucket efficiency
- **Data Collection Rate**: Records per minute
- **Error Frequency**: By error type and endpoint

## Performance Optimization

### Concurrent Processing

#### Async Implementation
```python
async def process_multiple_regions(regions):
    async with ClientSession() as session:
        tasks = [
            process_region(region, session) 
            for region in regions
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

#### Connection Pooling
- **aiohttp Session Reuse**: Single session per pipeline run
- **Connection Limits**: Configurable concurrent connections
- **DNS Caching**: Reduced lookup overhead

### Database Optimization

#### Batch Insertion
```python
def save_data(self, data: list):
    # Use SQLAlchemy bulk operations
    stmt = insert(self.table).values(data)
    stmt = stmt.on_conflict_do_nothing()
    session.execute(stmt)
```

#### Indexing Strategy
- **Primary Keys**: Composite keys on frequently joined columns
- **Foreign Keys**: Automatic indexing for relationships
- **Query Optimization**: Index on filtering columns

### Memory Management

- **Streaming Processing**: Process data in chunks
- **Generator Usage**: Avoid loading full datasets
- **Connection Cleanup**: Proper session management

## Troubleshooting

### Common Issues and Solutions

#### 1. API Key Issues

**Problem**: 401 Unauthorized responses
```
ERROR: HTTP 401: Missing authentication credentials
```

**Solution**:
```bash
# Verify API key format
echo $RIOT_API_KEY | grep "RGAPI-"

# Check key expiration at developer.riotgames.com
# Regenerate if necessary
```

#### 2. Rate Limiting Issues

**Problem**: Frequent 429 errors despite rate limiting
```
WARNING: HTTP 429: Rate limit exceeded
```

**Solutions**:
- Reduce concurrent requests
- Increase backoff time
- Check for multiple pipeline instances

#### 3. Database Connection Issues

**Problem**: SQLite database locked
```
ERROR: database is locked
```

**Solutions**:
```python
# Increase timeout
engine = create_engine('sqlite:///db.db', pool_timeout=30)

# Use WAL mode for better concurrency
connection.execute('PRAGMA journal_mode=WAL')
```

#### 4. Memory Issues

**Problem**: High memory usage during processing
```
MemoryError: Unable to allocate array
```

**Solutions**:
- Reduce batch size
- Enable streaming mode
- Increase system swap space

### Debug Mode

Enable detailed debugging:

```python
import logging
logging.getLogger('league_pipeline').setLevel(logging.DEBUG)

# Enable SQL query logging
engine = create_engine('sqlite:///db.db', echo=True)
```

## Contributing

### Development Setup

1. **Fork the Repository**
2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Run Tests**
   ```bash
   pytest tests/
   ```

5. **Code Quality Checks**
   ```bash
   flake8 league_pipeline/
   black league_pipeline/
   mypy league_pipeline/
   ```

### Contribution Guidelines

#### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings for all public methods
- Maximum line length: 88 characters

#### Testing Requirements
- Unit tests for all new functions
- Integration tests for API endpoints
- Mock external dependencies
- Maintain >90% code coverage

#### Documentation
- Update README for new features
- Add inline comments for complex logic
- Include usage examples

### Pull Request Process

1. **Description**: Clear description of changes
2. **Testing**: Include test results
3. **Documentation**: Update relevant docs
4. **Review**: Address all feedback
5. **Squash**: Clean commit history

## Advanced Topics

### Custom Data Transformations

#### Adding New Metrics

```python
# In match_data.py
def transform_results(self, data):
    # Add custom calculated metrics
    participant_data['custom_efficiency'] = (
        participant_data['gold_per_minute'] / 
        participant_data['deaths'] if participant_data['deaths'] > 0 else 0
    )
    return participant_data
```

#### Custom Filtering

```python
# Filter matches by duration
def filter_by_duration(self, match_data, min_duration=900):
    duration = match_data['info']['gameDuration']
    return duration >= min_duration
```

### Extending to New Game Modes

#### Adding ARAM Support

```python
class ARAMDataCollector(MatchDataService):
    def __init__(self):
        super().__init__()
        self.game_queue = 'ARAM'
        self.map_id = 12  # Howling Abyss
    
    def process_aram_specific_metrics(self, data):
        # ARAM-specific processing
        pass
```

### Performance Monitoring

#### Custom Metrics Collection

```python
import time
from prometheus_client import Counter, Histogram

api_calls = Counter('riot_api_calls_total', 'Total API calls')
response_time = Histogram('riot_api_response_seconds', 'Response time')

@response_time.time()
async def monitored_api_call(self, url):
    api_calls.inc()
    return await self.make_request(url)
```

### Production Deployment

#### Docker Configuration

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "scripts/run_pipeline.py"]
```

#### Environment Configuration

```bash
# Production environment variables
export RIOT_API_KEY="your-production-key"
export DATABASE_URL="postgresql://user:pass@host/db"
export LOG_LEVEL="INFO"
export RATE_LIMIT_BUFFER="0.8"  # Use 80% of rate limit
```

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Riot Games** for providing comprehensive API access
- **League of Legends Community** for inspiration and feedback
- **Open Source Contributors** who helped improve this project

---

*For additional support, please open an issue on GitHub or contact the maintainers.*