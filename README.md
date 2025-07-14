# 🧩 League of Legends Data Pipeline

A comprehensive data collection pipeline for League of Legends match data using the Riot Games API.

## ✨ What it does

Collects and stores League of Legends match data including:
- Player profiles across all tiers (Iron to Challenger)
- Detailed match information and statistics
- Frame-by-frame timeline events
- Team and participant performance data

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Valid Riot Games API key ([Get one here](https://developer.riotgames.com/))

### Installation

1. Clone the repository:
```bash
git clone https://github.com/PadTo/League-of-Legends-data-pipeline.git
cd League-of-Legends-data-pipeline
```

2. Install the package:
```bash
pip install .
```

3. Run the pipeline:
```bash
python main.py
```

You'll be prompted to enter your Riot API key on first run.

## ⚙️ Configuration

Edit `pipeline_configuration.json` to customize:

```json
{
  "players_per_tier": 5,
  "matches_per_tier": 100,
  "day_limit": 12,
  "stages_to_process": [1, 1, 1, 1],
  "database_save_location": "your/data/path"
}
```

**Key Settings:**
- `players_per_tier`: Number of players to collect per rank
- `matches_per_tier`: Number of matches to process per tier
- `day_limit`: Only collect matches from last N days
- `stages_to_process`: Enable/disable pipeline stages [summoners, matches, match data, timelines]

## 🗃️ Data Output

The pipeline creates an SQLite database with 5 tables:
- **Summoners**: Player profiles and rankings
- **Match_IDs**: Match identifiers and metadata
- **Match_Teams**: Team-level statistics
- **Match_Participants**: Individual player performance
- **Match_Timeline**: Frame-by-frame game events

Export to CSV using the included `LoLDatabaseQuery` class.

## 📊 Features

- **Smart Rate Limiting**: Respects Riot API limits with exponential backoff
- **Tier Classification**: Majority voting system for accurate match ranking
- **Selective Processing**: Run only the stages you need
- **Production Ready**: Comprehensive logging and error handling
- **Memory Efficient**: Configurable batch processing

## 🏗️ Project Structure

<pre>

league_pipeline/
├── config/
│   ├── __init__.py
│   ├── log_config.json
│   ├── pipeline_config.json
│   ├── riot_api_key.py
├── db/
│   ├── __init__.py
│   ├── db_interface.py
├── data_collection/
│   ├── __init__.py
│   ├── riot_api.py
├── pipeline/
│   ├── __init__py
│   ├── run_pipeline.py
├── riot_api/
│   ├── __init__.py
│   ├── riot_client.py
├── utils/
│   ├── __init__.py
│   ├── logger.py
├── __init__.py
logs/
notebooks/
├── playground.ipynb
photos/
│   ├── API_Call_Workflow.png
│   ├── Database_Tables_Relationships
.gitignore
README.md
setup.py

</pre>

## 🔧 Advanced Usage

For detailed configuration options, API workflow diagrams, and database schema documentation, see the [full documentation](documentation.txt).

### Common Use Cases

**Research/Analysis:**
```json
{
  "players_per_tier": 50,
  "matches_per_tier": 500,
  "day_limit": 7
}
```

**Quick Testing:**
```json
{
  "players_per_tier": 5,
  "matches_per_tier": 10,
  "day_limit": 3
}
```

## ⚠️ Important Notes

- **Processing Time**: Full data collection takes several hours due to API rate limits
- **European Regions Only**: Currently supports EUW/EUNE regions
- **API Key Required**: Valid Riot Games developer API key needed
- **Storage Space**: Full datasets can be several GB

## 🤝 Contributing

Issues and pull requests welcome! Please check the [documentation](documentation.txt) for development setup.

## 📝 License

This project is not affiliated with Riot Games. Use in accordance with Riot's API Terms of Service.

---

*For technical details, database schema, and API workflow diagrams, see the complete documentation.*