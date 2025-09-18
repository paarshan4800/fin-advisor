# FinAdvisor

A Python-based agentic AI app using Flask and LangChain for viewing user transactions with insights and recommendations.

## Tools

1. **Date Extractor**: Extracts dates from queries using LLM
2. **Mongo Query Filter Extractor**: Parses filters (dates, mode, currency, amount, status)
3. **Mongo Projection**: Generates minimal MongoDB projections for efficiency
4. **Mongo Query Tool**: Executes queries, caches results in Redis
5. **Category Mapper**: Categorizes spending, suggests savings
6. **Chart Data Preparer**: Creates visualizations

## Optimizations

- **Projections**: Fetches only required MongoDB fields.
- **Redis Caching**: Stores query results to avoid data flow between LLM and tools.
- **Selective Tool Calling**: Agent invokes only necessary tools.

## Screenshots

![Transactions Table](/assets/screenshots/transactions_table.png)
![Prompt Input](/assets/screenshots/prompt_input.png)
![Table Insights](/assets/screenshots/table_insights.png)
![Pie chart](/assets/screenshots/pie_chart.png)
![Bar chart](/assets/screenshots/bar_chart.png)