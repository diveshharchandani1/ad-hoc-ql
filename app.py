import streamlit as st
from langchain_ollama import ChatOllama
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain
import pymysql
from scripts.llm import ask_llm
from langchain_core.runnables import chain
import ast
from sqlalchemy import inspect

# Database configuration
def get_db_connection():
    # Use session state if available, else use secrets
    config = getattr(st.session_state, 'db_config', st.secrets.db)
    
    return SQLDatabase.from_uri(
        f"mysql+pymysql://{config['user']}:{config['password']}@"
        f"{config['host']}:{config['port']}/{config['name']}",
        sample_rows_in_table_info=3
    )

@st.cache_resource
def init_llm():
    return ChatOllama(
        model='llama3.2:3b',
        base_url='http://localhost:11434',
        temperature=0.7
    )

@st.cache_resource
def get_sql_chain(_llm, _db):
    def get_dynamic_schema_context(db):
        """Dynamically fetches schema information using SQLAlchemy inspector"""
        try:
            inspector = inspect(db._engine)
            tables = inspector.get_table_names()
            
            # Get current database name from connection
            current_db = db._engine.url.database
            
            schema_context = f"Database Schema Information for {current_db}:\n"
            for table in tables:
                schema_context += f"- `{table}`\n"
                
                # Get columns
                columns = inspector.get_columns(table)
                column_info = []
                for col in columns:
                    col_str = f"{col['name']} ({col['type']})"
                    if col.get('primary_key', False):
                        col_str += " PRIMARY KEY"
                    column_info.append(col_str)
                schema_context += "  - " + "\n  - ".join(column_info) + "\n"
                
                # Get foreign keys
                fks = inspector.get_foreign_keys(table)
                if fks:
                    schema_context += "  - Relationships:\n"
                    for fk in fks:
                        ref_table = fk['referred_table']
                        ref_columns = fk['referred_columns']
                        local_columns = fk['constrained_columns']
                        schema_context += f"    - FOREIGN KEY ({', '.join(local_columns)}) REFERENCES {ref_table}({', '.join(ref_columns)})\n"
            
            return schema_context
        except Exception as e:
            st.error(f"Error fetching schema: {str(e)}")
            return "Could not fetch schema information"

    # Custom context with dynamic schema
    CUSTOM_CONTEXT = f"""You are an expert SQL query generator. Follow these rules:
1. **Schema Awareness**: {get_dynamic_schema_context(_db)}
2. **Query Optimization**: Select only needed columns, use proper filters
3. **JOINs**: Use INNER JOIN for required relationships
4. **Aggregation**: Include GROUP BY with aggregate functions
5. **Filtering**: Always add LIMIT 5 unless specified
6. **Format**: Return ONLY SQL query, no explanations"""

    return create_sql_query_chain(_llm, _db) | (lambda query: {
        "context": CUSTOM_CONTEXT + "\nSchema:\n" + _db.get_table_info(),
        "question": query
    })

@chain
def get_correct_sql_query(input):
    context = input['context']
    question = input['question']

    instruction = f"""Use above context to fetch the correct SQL query for following question:
    {question}

    Do not enclose query in ```sql and do not write preamble and explanation.
    You MUST return only single SQL query."""

    return ask_llm(context=context, question=instruction)

# Streamlit UI
st.title("AD-HOC-QL")

# Add database connection sidebar
with st.sidebar:
    st.header("Database Connection")
    db_user = st.text_input("Username", value="root")
    db_password = st.text_input("Password", type="password")
    db_host = st.text_input("Host", value="localhost")
    db_port = st.number_input("Port", value=3306)
    db_name = st.text_input("Database Name", placeholder="mydb")
    
    # Add Test Connection button first
    if st.button("Test Connection"):
        try:
            # Attempt connection with current credentials
            connection = pymysql.connect(
                host=db_host,
                port=int(db_port),
                user=db_user,
                password=db_password,
                database=db_name
            )
            connection.close()
            st.success("✅ Connection successful!")
        except Exception as e:
            st.error(f"❌ Connection failed: {str(e)}")
    
    if st.button("Connect"):
        # Store credentials in session state
        st.session_state.db_config = {
            'user': db_user,
            'password': db_password,
            'host': db_host,
            'port': db_port,
            'name': db_name
        }
        st.success("Connection parameters saved!")

question = st.text_input("Enter your question about the data:", 
                        placeholder="What's your ad-hoc?")

# Add hidden instruction to every question
question += " You MUST RETURN ONLY MYSQL QUERIES."

if st.button("Generate Ad-Hoc Results"):
    st.cache_resource.clear()
    if not question:
        st.warning("Please enter a question first!")
        st.stop()
        
    with st.spinner("Processing your query..."):
        try:
            # Initialize components
            llm = init_llm()
            db = get_db_connection()
            sql_chain = get_sql_chain(llm, db)
            
            # Generate initial query
            raw_query = sql_chain.invoke({'question': question})
            
            # Get corrected query
            corrected_query = get_correct_sql_query.invoke({
                'context': raw_query,
                'question': question
            })
            
            # Execute and display results
            result = db.run(corrected_query)
            
            # Improved result handling for multiple rows
            st.write("Query Results:")
            try:
                # Handle list of tuples format from SQLDatabase
                if result.startswith("[(") and result.endswith(")]"):
                    rows = eval(result)
                    for row in rows:
                        if len(row) == 1:  # Single column
                            st.write(f"- {row[0]}")
                        else:  # Multiple columns
                            st.write(" | ".join(str(x) for x in row))
                else:
                    st.write(result)
            except:
                st.write(result)
            
        except Exception as e:
            st.error(f"Error processing query: {str(e)}")







