# Agentic AI Transaction Analyzer

## Overview

A Python-based agentic AI app using Flask and LangChain for transaction management and analysis. Features two modules:

1. **Transaction UI**: Paginated table with filters for user transactions (MongoDB read operations).
2. **AI Analysis**: Processes natural-language prompts (e.g., "Categorize my spendings in last 2 months") to generate visualizations (pie/bar/line charts or tables) with spending insights and savings recommendations.

## Features

- Paginated transaction table with filters.
- Natural-language query processing for analysis.
- Visualizations (charts/tables) with summaries.
- AI-driven spending categorization and savings tips.
- Optimized MongoDB queries using projections.
- Redis caching for efficient data handling.

## Tools

1. **Date Extractor**: Extracts ISO-8601 dates from queries using LLM.
2. **Mongo Query Filter Extractor**: Parses filters (dates, mode, currency, amount, status).
3. **Mongo Projection**: Generates minimal MongoDB projections for efficiency.
4. **Mongo Query Tool**: Executes queries, caches results in Redis.
5. **Category Mapper**: Categorizes spending, suggests savings.
6. **Chart Data Preparer**: Creates visualizations from cached data.

## Tech Stack

- **Backend**: Python, Flask
- **AI**: LangChain
- **Database**: MongoDB
- **Caching**: Redis
- **Visualizations**: Chart.js/Matplotlib

## Optimizations

- **Projections**: Fetches only required MongoDB fields.
- **Redis Caching**: Stores query results to avoid large data transfers.
- **Selective Tool Calling**: Agent invokes only necessary tools.

## Installation

1. Clone repo:
   ```
   git clone https://github.com/yourusername/agentic-ai-transaction-analyzer.git
   cd agentic-ai-transaction-analyzer
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set environment variables (`.env`):
   ```
   MONGODB_URI=your_mongodb_uri
   REDIS_URL=your_redis_url
   LANGCHAIN_API_KEY=your_langchain_key
   ```

4. Run:
   ```
   flask run
   ```

## Usage

- **UI**: Visit `http://localhost:5000/` for transaction table.
- **AI Analysis**: Enter prompts at `/analyze` (e.g., "Show pie chart of last 2 months' expenses").

## License

MIT License. See [LICENSE](LICENSE).