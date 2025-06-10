# Face Recognition Attendance System

An automated attendance tracking system built with Python that uses facial recognition to identify individuals and record their attendance in a database.

## Features

- **Accurate Face Recognition**: Powered by the face_recognition library for reliable identification
- **Real-time Processing**: Live camera feed analysis with instant feedback
- **Modern UI**: Clean and intuitive interface built with PyQt6
- **Asynchronous Design**: Non-blocking architecture using qasync for smooth performance
- **Secure Storage**: All attendance records stored in a MySQL database
- **Easy Management**: Simple tools for adding and managing personnel
- **Flexible Implementation**: Suitable for educational, corporate or event settings

## Project Structure

- `main.py` - Main application entry point
- `EncodeGenerator.py` - Generates facial encodings from images
- `AddDatatoDatabase.py` - Tool for adding employee data to the database
- `Images/` - Contains reference facial images for recognition
- `data/` - Stores application data including encoded images
- `database/` - Database connection utilities
- `gui/` - PyQt6 GUI implementation
- `Helper/` - Helper functions and utilities
- `recognition/` - Face recognition implementation
- `utils/` - Utility functions and classes

## Requirements

- Python 3.11+
- MySQL Server
- Libraries:
  - face_recognition
  - opencv-python (cv2)
  - PyQt6
  - qasync
  - numpy
  - mysql-connector-python

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv myenv
   ```
3. Activate the virtual environment:
   - Windows: `myenv\Scripts\activate`
   - Linux/Mac: `source myenv/bin/activate`
4. Install required packages:
   ```
   pip install -r requirements.txt
   ```
5. Set up a MySQL database named `face_recognition`
6. Add reference images to the `Images` folder with filenames as employee/student IDs (e.g., `123456.jpg`)

## Usage

1. Add employee/student data:
   ```
   python AddDatatoDatabase.py
   ```

2. Generate facial encodings:
   ```
   python EncodeGenerator.py
   ```

3. Run the main application:
   ```
   python main.py
   ```

## Database Setup

The system requires a MySQL database named `face_recognition` with an `employee` table. The table structure is automatically created when running `AddDatatoDatabase.py`.

## Adding New Individuals

1. Add a photo of the person to the `Images` directory with their ID as the filename (e.g., `123456.png`)
2. Run `EncodeGenerator.py` to update the facial encodings
3. Add their information to the database using `AddDatatoDatabase.py`

## License

[MIT License](LICENSE)
