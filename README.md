# A11y VisionRover with Near-RealTime Vision & Speech

A11yVisionRover is a real-time robotics application that integrates computer vision and text-to-speech capabilities. Using a Viam-based robot, this program captures images of its environment, processes them with OpenAI's GPT-4 to generate concise room descriptions, and converts these descriptions to speech. The application also includes a follow mode where the robot tracks objects in its field of view.

## Features

- **Autonomous Robot Movement:** Move the robot using object detection on a color set pre-defined (can be improved).
- **Computer Vision:** Rotate and capture multiple images to analyze room layout.
- **AI Room Description:** Use OpenAI's GPT-4 to describe the room.
- **Text-to-Speech:** Convert text descriptions to speech.
- **Interactive Commands:** Use keyboard input to trigger actions such as capturing images or quitting the program.

## Installation

### Prerequisites

Ensure you have the following installed:

- Python 3.8+
- `pip` package manager
- Viam robot with API access
- OpenAI API key

### Clone the Repository

```bash
git clone https://github.com/zii-bee/a11yvisionrover.git
cd a11yvisionrover
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Set Up Environment Variables

Create a `.env` file in the root directory and add the following:

```
OPENAI_API_KEY=your_openai_api_key
VIAM_API_KEY=your_viam_api_key
VIAM_API_KEY_ID=your_viam_api_key_id
ROBOT_ADDR=your_robot_address
```

## Usage

### Running the Application

```bash
python main.py
```

### Controls

- **Press `1` + Enter:** Capture images and generate a room description.
- **Press `q` + Enter:** Quit the program.

## Project Structure
Create a virtual environment upon installation using the steps described below. 
```
a11yvisionrover/
├── venv             # Library installations
├── config.py        # Configuration file for API keys and robot address
├── capture.py       # Handles image capture and robot rotation
├── vision_utils.py  # Vision processing and image analysis
├── speech.py        # Text-to-speech conversion
├── follow.py        # Object following logic
├── main.py          # Main script to run the application
├── requirements.txt # Dependencies
├── README.md        # Project documentation
└── .env             # Environment variables (not tracked in version control)
```

## How It Works

1. **Robot Movement & Image Capture:** The robot captures multiple images while rotating to provide a comprehensive view of the room.
2. **AI-Powered Room Description:** The captured images are processed and analyzed using OpenAI’s GPT-4.
3. **Text-to-Speech:** The generated description is converted into speech using OpenAI’s TTS model.
4. **Object Tracking:** The robot continuously monitors its environment and follows detected objects.

## Troubleshooting

### OpenAI API Errors

- Ensure your API key is correct and has sufficient usage limits.
- Check if OpenAI services are operational.

### Viam Robot Connection Issues

- Verify the robot's address and API credentials in the `.env` file.
- Restart the robot and check the network connection.

### Audio Playback Issues

- Ensure your system supports `pyaudio`.
- Use `pip install pyaudio` (Windows users may need additional setup).

## Future Enhancements

- **Voice Commands:** Allow voice-based interaction with the robot.
- **Enhanced Object Recognition:** Improve object tracking with ML models.
- **Autonomous Navigation:** Enable the robot to move intelligently based on room layout.

## License

This project is licensed under the MIT License. See `LICENSE` for details.

## Contributors

- [zii-bee](https://github.com/zii-bee)

## Acknowledgments

- OpenAI for GPT-4 and TTS models
- Viam for the robotics framework

