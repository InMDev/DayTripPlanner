# DayTripPlanner

## Overview

This Flask application is designed to help users select optimal activities based on budget and time constraints using linear programming techniques. It provides a web interface where users can input their constraints and preferences, and the application computes the best combination of activities to maximize value while adhering to the constraints.

### Live Demo
[Link Here](https://dayplanner-vifc.onrender.com/)
Note: Due to free plan, might take longer in the first launch.

### A Mathematical Perspective into it
[Explained in my Notion Page](https://www.notion.so/inzaghi/Optimize-dating-plan-in-Vancouver-Artifact-1-17e2b6100f324c9bb6b8ba8c14c2d956)

## Setup

### Prerequisites

- Python 3.x installed
- Flask framework (`pip install Flask`)
- OR-Tools library (`pip install ortools`)

### Installation

1. Clone this repository:
   ```
   git clone <repository_url>
   cd <repository_name>
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

To start the Flask server, run the following command:
```
python app.py
```

By default, the application will be accessible at `http://localhost:5000`.

## Usage

1. **Homepage (`/`)**: Displays a basic HTML form for user input.

2. **Submission Endpoint (`/submit/<string:string_activities>`)**: Accepts a POST request containing budget and time constraints, as well as a string representation of activities. It processes these inputs and computes the optimal set of activities using a linear programming model implemented with OR-Tools.

3. **Output**: Upon successful computation, the application displays a list of recommended activities that fit within the provided budget and time constraints. If no optimal solution is found, an appropriate message is displayed.

## Project Structure

- **app/**
  - **routes.py**: Defines Flask routes, including logic for handling user input, invoking the linear programming model, and rendering the results.
  - **templates/**: Contains HTML templates used to render pages.

## Example

Here's an example of how to use the application:

1. Navigate to `http://localhost:5000`.
2. Fill out the form with your budget, time constraints, and activities.
3. Submit the form.
4. The application will display the optimal activities that maximize value within your constraints.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvement, please open an issue or a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

---

Feel free to expand on any sections or add additional details specific to your project. This README should provide a good starting point for users and developers who want to understand, install, and use your Flask application for activity selection optimization.
