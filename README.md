# AI Vehicle Comparison System

## Overview
The AI Vehicle Comparison System serves as a sophisticated platform for conducting intelligent vehicle comparisons and uncovering local advertisements specific to the Sri Lankan market. Our architecture integrates a robust FastAPI backend service with a dynamic Next.js frontend application, ensuring comprehensive vehicle analysis powered by advanced machine learning models and automated web scraping technologies.

---

## Backend

### Features
- **AI-Powered Analysis**: Harnesses the capabilities of Google Gemini 1.5-flash and CrewAI agents for advanced intelligent vehicle comparisons.
- **Smart Web Scraping**: Leverages automated processes to discover vehicle listings from leading Sri Lankan websites.
- **Real-time Data**: Provides live data analysis and market insights with remarkable accuracy.
- **RESTful API**: Features extensively documented endpoints, facilitating seamless integration through OpenAPI/Swagger.

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
   - Install dependencies using `uv pip install -r requirements.txt`.
   - Configure environment variables in a `.env` file.

4. **Run the Backend Server**:
   ```bash
   uvicorn app.main:app --reload --port 8080
   ```

### Key Technologies
- **FastAPI**: A high-performance framework for creating APIs with Python.
- **CrewAI**: An orchestration framework to manage complex multi-agent workflows.
- **SQLAlchemy**: Provides a robust ORM for seamless database interactions.
- **SQLite**: Acts as a lightweight yet powerful database for storing advertisements.

---

## Frontend

### Features
- **React with Next.js**: Employs a modern framework for server-side rendering and static site generation.
- **Tailwind CSS and FontAwesome**: Utilized for highly customizable styling and iconography.
- **Responsive Design**: Adaptively scales across diverse device dimensions and orientations.

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
   Launch the application by visiting `http://localhost:3000`.

### Key Technologies
- **Next.js**: A powerful React framework known for optimized server-rendered applications.
- **React**: The de-facto library for building user interfaces.
- **Tailwind CSS & FontAwesome**: Enriches the UI with scalable styling and comprehensive icon support.

---

## Contributing
We welcome contributions and are eager to collaborate! Please refer to our contribution guidelines for further details.

## License
Licensed under the MIT License, ensuring open and free usage in both commercial and non-commercial projects.
