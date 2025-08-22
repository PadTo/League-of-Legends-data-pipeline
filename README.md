# League of Legends Data Pipeline

A comprehensive, production-ready data pipeline for collecting and analyzing League of Legends match data using the Riot Games API with intelligent rate limiting and async processing.

For the full detailed documentation go [HERE]:(https://github.com/PadTo/League-of-Legends-data-pipeline/tree/main/docs)

## 🚀 Features

- **Multi-Region Data Collection**: Supports all League regions with continental grouping
- **Intelligent Rate Limiting**: Token bucket algorithm respects Riot API limits
- **Async Processing**: High-performance concurrent API calls with error handling
- **Comprehensive Data Collection**: 
  - Summoner rankings and profile data
  - Match IDs with time-based filtering
  - Detailed match statistics and participant data
  - Timeline events with positioning data
- **Robust Database Design**: SQLite with proper normalization and foreign key relationships
- **Production Features**: Exponential backoff retries, comprehensive logging, and error handling

## 📊 Data Pipeline Stages

1. **Summoner Collection**: Gather ranked players from all tiers and regions
2. **Match ID Collection**: Retrieve recent match histories with tier validation
3. **Match Data Collection**: Collect detailed statistics, objectives, and KDA data
4. **Timeline Collection**: Gather timestamped events and player positioning

## 🛠️ Tech Stack

- **Python 3.8+** with asyncio for concurrent processing
- **aiohttp** for async HTTP requests  
- **SQLAlchemy** ORM with SQLite database
- **Token Bucket Rate Limiting** for API compliance
- **Riot Games API** integration

## 📈 Use Cases

- **Esports Analytics**: Professional team and player performance analysis
- **Game Balance Research**: Meta trends and champion win rate analysis
- **Academic Research**: Large-scale gaming behavior and strategy studies
- **Personal Analytics**: Rank progression and gameplay improvement tracking

## 🚦 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/league-data-pipeline.git
cd league-data-pipeline

# Install dependencies
pip install -r requirements.txt

# Set up your Riot API key
python -c "from league_pipeline.key.key_handler import set_api_key; set_api_key('YOUR_API_KEY')"

# Configure pipeline stages in constants/pipeline_constants.py
# Then run the pipeline
python -c "from league_pipeline.pipeline.orchestrator_pipeline import PipelineOrchestrator; PipelineOrchestrator().run_full_pipeline()"
```

## 📋 Requirements

- Python 3.8+
- Riot Games API key ([Get one free](https://developer.riotgames.com))
- ~2GB free disk space for database storage

## 🔧 Configuration

The pipeline is highly configurable through constants:
- **Regions**: Select which regions to process
- **Tiers**: Configure rank tiers to collect (Iron to Challenger)
- **Time Limits**: Set data collection time windows
- **Processing Stages**: Enable/disable pipeline components

## 📄 License

MIT License - see LICENSE file for details.

---

