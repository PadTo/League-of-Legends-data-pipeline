# League of Legends Data Pipeline

A comprehensive, scalable data pipeline for collecting and analyzing League of Legends match data using the Riot Games API.

## 🚀 Features

- **Multi-Region Support**: Collect data from all League of Legends regions
- **Intelligent Rate Limiting**: Token bucket implementation respects Riot API limits
- **Async Processing**: High-performance concurrent API calls
- **Comprehensive Data Collection**: 
  - Player/Summoner information
  - Match IDs and metadata
  - Detailed match statistics
  - Timeline events and positioning data
- **Robust Database Design**: SQLite with proper normalization and relationships 
- **Production-Ready**: Error handling, retries with exponential back-off, and logging

## 📊 Data Collected

- **Summoner Data**: Rankings, regions, tiers, divisions
- **Match Statistics**: KDA, gold, damage, vision, objectives
- **Timeline Events**: Kills, objectives, positioning over time
- **Team Performance**: Win/loss, objectives, team compositions

## 🛠️ Tech Stack

- **Python 3.8+** with asyncio for concurrent processing
- **aiohttp** for async HTTP requests
- **asyncio** for async processing
- **SQLAlchemy** for database ORM
- **SQLite** for data storage (adjustable)
- **Riot Games API** for data source

## 📈 Use Cases

- **Esports Analytics**: Team and player performance analysis
- **Game Balance Research**: Meta analysis and champion statistics
- **Academic Research**: Large-scale gaming behavior studies
- **Personal Projects**: Rank analysis, improvement tracking

## 🚦 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/league-of-legends-data-pipeline.git

# Install dependencies
pip install -r requirements.txt

# Set up your Riot API key
echo "RIOT_API_KEY=your_api_key_here" > league_pipeline/key/api_key.env

# Run the pipeline
python scripts/run_pipeline.py
```

## 📋 Requirements

- Python 3.8+
- Riot Games API key (free at [developer.riotgames.com](https://developer.riotgames.com))
- ~1GB free disk space for database

## 📄 License

MIT License - see LICENSE file for details.

---

⭐ **Star this repo if you find it useful!**