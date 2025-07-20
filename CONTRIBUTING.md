# Contributing to TCG Analytics

Thank you for your interest in contributing to TCG Analytics! This document provides guidelines and instructions for contributing to the project.

## Prerequisites

- Python 3.9+
- Poetry (Python dependency manager)
- Git

## Getting Started

### 1. Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/tcg-analytics.git
   cd tcg-analytics
   ```

### 2. Set Up Development Environment

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Activate the virtual environment:**
   ```bash
   poetry shell
   ```

4. **Set up environment variables:**
   ```bash
   export JUSTTCG_API_KEY=your_api_key_here
   ```

### 3. Running the Application

**Start the development server:**
```bash
poetry run python src/api/main.py
```

The API will be available at `http://localhost:8000`

**Alternative using uvicorn:**
```bash
poetry run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Development Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Keep functions small and focused

### Testing
- Add tests for new functionality
- Run existing tests to ensure nothing breaks:
  ```bash
  poetry run python util/justtcg_test.py
  ```

### Error Handling
- Add appropriate error handling for new endpoints
- Use FastAPI's HTTPException for API errors
- Include meaningful error messages

### API Development
- Follow RESTful conventions
- Document new endpoints
- Use appropriate HTTP status codes
- Validate input parameters

## API Endpoints

- `GET /api/v1/health_check` - Health check endpoint
- `GET /api/v1/cards/{card_id}` - Get card information by TCGPlayer ID

### Testing API Endpoints

Once the server is running, you can test the endpoints using curl:

**Health Check:**
```bash
curl http://localhost:8000/api/v1/health_check
```

**Get Card Information:**
```bash
curl http://localhost:8000/api/v1/cards/12345
```

Replace `12345` with an actual TCGPlayer card ID. Make sure you have set the `JUSTTCG_API_KEY` environment variable before testing card endpoints.

## Submitting Changes

1. **Create a new branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and commit:**
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

3. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request** on GitHub with:
   - Clear description of changes
   - Reference to any related issues
   - Test results

## Reporting Issues

When reporting issues, please include:
- Steps to reproduce the problem
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Error messages or logs

## Questions?

If you have questions about contributing, please open an issue for discussion.