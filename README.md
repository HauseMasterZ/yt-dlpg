# yt-dlpg

<p align="center">
  <img src="https://github.com/HauseMasterZ/yt-dlpg/assets/113833707/e7e24925-ad5b-40b9-b9ed-72db1a1aac57" alt="Home Page"/>
</p>

## Overview

**yt-dlpg** is a powerful yet easy-to-use YouTube downloader. It allows you to download videos in various formats and includes features such as auto-start and archive file tracking to avoid duplicate downloads.

### Note:
If the downloaded file format differs from the one you selected, it means the specified format is unavailable. The program will automatically choose the next best available format.

## Installation

### Portable File or Install Executable
You can either use the portable file or install the executable version of yt-dlpg.

### Cloning the Repository and Installing Dependencies
Clone the repository and install the required dependencies listed in `requirements.txt` using the following command:

```bash
pip install -r requirements.txt
```

## Features

### Auto Start
This feature creates a shortcut to the batch script file in the default OS startup directory. To remove the shortcut, simply uncheck the box and hit download.

### Archive File
The archive file keeps track of downloaded files to prevent duplicate downloads. It creates a text file in the parent directory that contains the list of all downloaded media.

## Usage

### Basic Usage
1. **Download Video**: Select the desired format and hit the download button.
2. **Auto Start**: Enable auto start if you want the program to run automatically on system startup.
3. **Archive File**: Ensure the archive option is enabled to keep track of your downloads.

### Troubleshooting
- **Format Issues**: If the file format you selected is not available, the program will select the next best available format automatically.
- **Duplicate Downloads**: Use the archive file feature to avoid downloading the same media multiple times.

## Contribution
Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact
For any queries or issues, please open an issue on GitHub.