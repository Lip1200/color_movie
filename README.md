# Movie List and AI Recommendation App

## Description
This project allows users to create personalized movie lists and receive real-time movie recommendations powered by AI. The recommendations adapt based on the content of the movie list as users add films, making suggestions more accurate over time.

This app is a second-year Bachelor's project and is composed of two main services: a Next.js front-end and a Flask back-end, both containerized via Docker. The back-end handles data with MySQL and provides AI recommendations using ChromaDB.

## Features
- **Create Movie Lists**: Users can create and manage movie lists.
- **AI-Powered Recommendations**: The app suggests movies based on the current list and refines recommendations dynamically.
- **MySQL Database**: All movie and user data are stored in a MySQL database.
- **Dockerized**: Both the front-end and back-end run in Docker containers for easy setup and deployment.

## Project Structure
- **Next.js**: Front-end framework for rendering the UI.
- **Flask**: Back-end service providing API endpoints and handling business logic.
- **ChromaDB**: AI model for real-time, adaptive movie recommendations.
- **MySQL**: Database for storing movie and user information.

## Docker Setup
This project is built with Docker, and the services can be started using Docker Compose. Here's a breakdown of the services:

- **nextjs**: Next.js front-end service (port 3000).
- **flask**: Flask back-end service (port 5001), interacts with MySQL and ChromaDB.
- **db**: MySQL database service (port 3306), initialized with a `MovieDb.sql` script.
- **chromadb**: AI service for recommendations (port 8000).

### Docker Compose Configuration
To start the app, use the following commands:
```bash
docker-compose up
```
This will launch all services and make the application accessible at `http://localhost:3000`.

## Environment Variables
- `NEXT_PUBLIC_API_URL`: URL for the Flask back-end.
- `SQLALCHEMY_DATABASE_URI`: Connection string for MySQL.
- `CHROMADB_URI`: URL for the ChromaDB service.
- `JWT_SECRET_KEY`: Secret key for authentication.

## Installation and Usage
1. Clone the repository:
   ```bash
   git clone https://github.com/Lip1200/color_movie.git
   cd color_movie
   ```
2. Set up environment variables in `.env` files for both services.
3. Start the services with Docker Compose:
   ```bash
   docker-compose up
   ```
4. Access the app at `http://localhost:3000`.

## Future Enhancements
- Expand the AI model for more complex recommendations.
- Add user-specific profiles for personalized movie recommendations.

## License
This project is licensed under the MIT License.

