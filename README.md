# 1001-ScoreTracker

## Overview
This application is a score tracker for the card game "1001". It allows two players to input their names and scores, track the dealer's turn, and save or resume the game at any point. The app is built using PyQt5 for the GUI and provides functionality for score management, accusations, and game saving.

## Features
- Input player names
- Track the score of two players
- Display a score table and current game status
- Save the game progress
- Resume suspended games
- Handle accusations during the game
- Supports Mac and Linux platforms

## Prerequisites
Before running this application, make sure you have **Conda** or **pip** and Python 3 installed on your system. **It is preferable to use Conda**, as it simplifies package management and environment setup. However, installation with pip is also supported.

### Step 1: Install Conda and create a Conda Environment (Recommended)
#### Install Conda
1. **Install Miniforge** (lightweight Conda version):
   - Download Miniforge from [here](https://github.com/conda-forge/miniforge).
   - Install Miniforge by following the instructions provided in the documentation for your system.

If you don't want to use Conda, you can proceed with the **pip** installation steps.

#### Create a Conda Environment

1. Open a terminal (Mac or Linux).
2. Create a new Conda environment for the application:

   ```bash
   conda create -n score-tracker python=3.8
   ```

   This creates an isolated environment named `score-tracker` with Python 3.8.

3. Activate the environment:

   ```bash
   conda activate score-tracker
   ```

If you are not using Conda, you can skip the Conda-related steps and proceed directly to the pip installation section.

## Installation Instructions

### Option 1: Using Conda (Preferred)

1. Install the required dependencies (PyQt5 and other libraries):

   ```bash
   conda install pyqt=5
   ```

   This installs the latest version of PyQt5 along with the necessary dependencies.

2. Install `Pillow` for image handling (used for displaying the cover image):

   ```bash
   conda install pillow
   ```

### Option 2: Using pip (Alternative)

1. If you're using **pip** instead of Conda, first ensure that you have a Python virtual environment set up, or you can install the dependencies globally.

2. Install the required dependencies:

   ```bash
   pip install pyqt5
   pip install pillow
   ```

### Step 3: Set Up the Application

1. Clone or download the repository containing the source code of the application.
2. Ensure the following files are in the same directory:
   - `1001.py` (the main application file)
   - `copertina.png` (the cover image used in the UI)
   - `partite/` folder (to store suspended games)

### Step 4: Running the Application

1. In the terminal, navigate to the directory where the `1001.py` file is located.
2. Run the application:

   ```bash
   python 1001.py
   ```

   This will launch the PyQt5 application in a new window where you can start playing the game.

### Step 5: Saving and Resuming Games

- **Saving the game**: You can save your progress at any point during the game. The game will be saved as a CSV file in the `partite/` directory.
- **Resuming the game**: If you wish to resume a suspended game, click the "Partite in sospeso" button to load and continue your last saved game.

## Troubleshooting

- **Missing dependencies**: If you encounter issues with missing dependencies, try installing them with Conda or pip:

   ```bash
   conda install <package-name>
   ```

   Or with pip:

   ```bash
   pip install <package-name>
   ```

## Contributors 
- DeepSeek
- Leonardo Ignazio Pagliochini