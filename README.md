# 🧩 League of Legends Data Pipeline

> **Status**: In Development  
> **Purpose**: Automated, configurable data pipeline for fetching, filtering, and storing *League of Legends* match data using Riot's official API.

---

## 🔍 Overview

This repository contains a modular, rate-limited, and well-logged data pipeline built around the [Riot Games API](https://developer.riotgames.com/). It automates the process of:

- Retrieving ranked match data across tiers and roles
- Filtering relevant events and timelines
- Storing structured results in a local SQLite database
- Preparing clean datasets for statistical analysis and machine learning

---

## 🏗️ Folder Structure



---

## ⚙️ Features

### 🔗 Riot API Wrapper
- Graceful HTTP error handling with custom exceptions
- Region-based endpoints (EUW, Europe-wide match history)
- Tier & division queries (`CHALLENGER`, `DIAMOND`, etc.)
- Match ID fetching, summoner details, PUUID conversion

### 🚀 Pipeline Controller
- Automatic tier & player loop
- Built-in rate-limiting for API safety
- Structured SQLite data storage
- Timeline/event filtering (kills, jungle, objectives)
- Customizable event filtering via `eventTypesToConsider`

### 🧼 Data Filtering (Pluggable)
- Filter JSON payloads from `/timeline` endpoints
- Extract game-level features like:
  - First blood, dragons, baron, towers
  - Player movements & kill zones
  - Jungle tracking by timestamp

---
## 🧪 How to Run

```bash
# Clone repo
git clone https://github.com/yourusername/lol-data-pipeline.git

# Set up environment
pip install -r requirements.txt

# Add your Riot API Key
echo "RIOT_API_KEY=your_api_key_here" > riot_key_folder/riot_api_key.py

# Run the pipeline
python pipeline_workflow.py
