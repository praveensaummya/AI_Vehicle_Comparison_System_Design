# AI Vehicle Comparison System

## Overview
The AI Vehicle Comparison System is a comprehensive tool for intelligently comparing vehicles and discovering local advertisements in the Sri Lankan market. It features a FastAPI backend service and a Next.js frontend application, designed to work together seamlessly to provide insight into vehicle analysis through Advanced Machine Learning models and automated web scraping.

---

## Backend

### Features
- **AI-Powered Analysis**: Utilizes Google Gemini 1.5-flash and CrewAI agents for intelligent vehicle comparisons.
- **Smart Web Scraping**: Automated discovery of vehicle listings from popular Sri Lankan websites.
- **Real-time Data**: Live price analysis and market insights.
- **RESTful API**: Well-documented endpoints with OpenAPI/Swagger integration.

### Quick Start
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/AI_Vehicle_Comparison_System_Design.git
   ```

2. **Navigate to the Backend Directory**:
   ```bash
   cd backend
   ```

3. **Set up the Environment**:
   - Create and activate a virtual environment.
   - Install dependencies via `uv pip install -r requirements.txt`.
   - Configure environment variables in a `.env` file.

4. **Run the Backend Server**:
   ```bash
   uvicorn app.main:app --reload --port 8080
   ```

### Key Technologies
- **FastAPI**: For developing the API.
- **CrewAI**: For orchestrating multi-agent workflows.
- **SQLAlchemy**: For ORM and database management.
- **SQLite**: As the database for storing advertisements.

---

## Frontend

### Features
- **React with Next.js**: Offers a modern development environment with efficient Hot Module Replacement.
- **Tailwind CSS and FontAwesome**: For stylistic decisions and icon usage.
- **Responsive Design**: Optimized for different device sizes and screen orientations.

### Quick Start
1. **Navigate to the Frontend Directory**:
   ```bash
   cd frontend
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   ```

3. **Run the Development Server**:
   ```bash
   npm run dev
   ```

4. **Open in Browser**:
   Access the application at `http://localhost:3000`.

### Key Technologies
- **Next.js**: For server-rendered and static websites.
- **React**: For building user interfaces.
- **Tailwind CSS & FontAwesome**: For styling and icons.

---

## Contributing
We welcome contributions! Please see the contribution guidelines for more details.

## License
This project is licensed under the MIT License.
