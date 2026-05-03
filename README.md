# Golf Rival - Data Engineering



## Overview

This project implements a data engineering CLI application for processing raw event data from a game (Golf Rival) and computing analytical outputs for users and maps.
The application processes JSONL data by loading, cleaning, validating, reconstructing sessions and matches, and computing final aggregated results.

The idea is to simulate a simplified data analysis engine.



## Structure

The project is split into three logical parts:

### 1. Loader - loader.py

- loads raw data (events and maps)
- performs basic validation (checking required keys)
- filtering and keeping only valid data

### 2. Cleaner - cleaner.py

- removes duplicate events (id has to be unique), keeping earliest timestamp
- validates events based on event type
- consistency checks (event_data structure, timestamp validation, deviceOS validation)

### 3. Core - core.py
- builds output ready data models
- computes analytics (user-stats, map-stats)



## Output

### User Stats
Each user includes:
- username
- country
- registration date
- total playtime
- total win ratio
- average matches per session
- favorite map
- favorite map win ratio

### Map Stats
For each date:
- match count
- average playtime per map
- best player up to that date



## Key Decisions

- Duplicate events are resolved by keeping the earliest timestamp
- Self-matches are excluded by enforcing user_id != opponent_id constraint
- A session ends if more than 120 seconds pass between two session_ping events
- A match is considered valid if it contains at least one match_start and match_finish event
- Match reconstruction is simplified by selecting the earliest match_start and latest match_finish event per match group
- Matches are reconstructed by grouping events by players and map_id
- Best player is calculated using overall win and match counts, and for each date we select the player with the best win ratio based on all matches played up to that day
- Draw outcomes (0.5) are handled by not assigning a winner (winner is set to None), meaning they do not contribute to win statistics
- A CLI-based approach was chosen for simplicity, and pandas was used to format and display tabular output in a structured and readable way



## Entry Point (main.py)

The main.py file is the main file of the application.
It loads the data, runs the full processing logic, and provides CLI commands for getting user and map statistics.



## How to run

This project requires:
- Python 3
- pandas library

### Installation (on Ubuntu/Debian systems):
sudo apt update
sudo apt install python3 python3-pandas

### Run
Commands are executed in terminal from the project root using Python 3:

#### User Stats
python3 main.py user-stats

#### Map Stats
python3 main.py map-stats <map-name>



## Project Structure

project/
- main.py
- data/
  - events.jsonl
  - maps.jsonl
- logic/
  - loader.py
  - cleaner.py
  - core.py
