# AD-HOC-QL: Natural Language to SQL Converter

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-00ADD8?style=for-the-badge)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-7C3AED?style=for-the-badge)

AD-HOC-QL is a Streamlit-based application that converts natural language questions into SQL queries using Ollama's Llama3 3B model. Designed for ad-hoc database queries, it supports MySQL databases and provides an intuitive interface for non-technical users.

## Features ✨

- **Natural Language to SQL Conversion**: Transform plain English questions into executable SQL queries
- **Dynamic Schema Awareness**: Automatically detects database structure and relationships
- **Query Optimization**: Generates optimized queries with proper joins and filters
- **Query Correction**: Secondary LLM validation for SQL correctness
- **Multi-Database Support**: Connect to any MySQL database with configurable credentials
- **Result Visualization**: Displays query results in an easy-to-read format
- **Local LLM Integration**: Uses Ollama-hosted Llama3 3B model for privacy-focused processing

## Prerequisites 📋

- Python 3.10+
- Ollama running locally with Llama3.2 3B model
- MySQL database (version 8.0+ recommended)
- Streamlit for web interface

## Installation 🛠️

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ad-hoc-ql.git
cd ad-hoc-ql
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start Ollama service:

```bash
ollama serve
```

## Usage 🚀

1. Start the Streamlit app:

```bash
streamlit run app.py
```

2. In the sidebar:
   - Enter database credentials
   - Click "Test Connection" then "Connect"

3. In the main interface:
   - Enter your natural language question
   - Click "Generate Ad-Hoc Results"

Example question:

```text
"Show me all Nike t-shirts in black color with size XL"
```

## Architecture 🏗️

```mermaid
graph TD
    A[DB Connection] --> B[(Context Preparation)]
    B --> C{Selected Tables}
    C --> D[Schema Info<br>(db.getinfo)]
    D --> E[Table Relations<br>(SQLAlchemy)]
    E --> F[LLM Prompt Context]
    F --> G[User Question]
    G --> H{LLM Processing}
    H --> I[SQL Generation]
    I --> J[Query Correction]
    J --> K[Database Execution]
    K --> L[Result Visualization]
```

## Configuration ⚙️

Customize in `scripts/llm.py`:
- `base_url`: Ollama server URL
- `model`: LLM model selection
- `temperature`: Creativity control (0-1)

Customize in `app.py`:
- Default database credentials
- Schema sampling settings
- Query result formatting

## Limitations ⚠️

1. Requires local Ollama instance with sufficient RAM (8GB+ recommended)
2. Best performance with simple-to-moderate schema complexity
3. Limited to MySQL databases
4. Response speed depends on local hardware capabilities

## Contributing 🤝

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request



