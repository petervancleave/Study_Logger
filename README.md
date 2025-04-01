![image](https://github.com/user-attachments/assets/61b2e9e7-958f-4ec4-8ed7-c4caf2870dd8)


![image](https://github.com/user-attachments/assets/6aaf610c-9515-4dbe-855d-330abdf669e1)


## Features

- Dark-themed UI
- Track study sessions with start/stop functionality
- View total time spent learning
- Persistent storage using SQLite database

## Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
cd study-logger
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running from Source
```bash
python main.py
```

### Creating an Executable
To create a standalone executable:
```bash
pip install pyinstaller
pyinstaller --name "Study Logger" --windowed --onefile main.py
```
The executable will be created in the `dist` directory.

## Data Storage
- Study sessions are stored in a local SQLite database (`tracker.db`)
- The database is automatically created when you first run the application

## Development
- Built with PySide6 (Qt for Python)
- Uses SQLite for data storage
- Dark theme with modern styling

## Achievements

- Coming Soon
(More achievements can be added by modifying the database directly)
