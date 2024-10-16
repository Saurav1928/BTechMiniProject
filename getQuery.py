# import csv
# from collections import Counter

# def load_csv(file_path):
#     """Load the CSV file and return a list of (question, query) tuples."""
#     with open(file_path, mode='r', encoding='utf-8') as file:
#         reader = csv.reader(file)
#         next(reader)  # Skip header if there's one
#         return [(row[0], row[1]) for row in reader]

# def count_matching_words(input_question, natural_question):
#     """Count the number of matching words between two questions."""
#     # Tokenize the questions into words
#     input_words = set(input_question.lower().split())
#     natural_words = set(natural_question.lower().split())
    
#     # Find the intersection of words
#     matching_words = input_words.intersection(natural_words)
#     return len(matching_words), matching_words

# def find_best_query(input_question, csv_file_path):
#     """Find the SQL query with the maximum matching words for the input question."""
#     # Load the CSV data
#     data = load_csv(csv_file_path)
    
#     max_matches = 0
#     best_natural_question = None
#     best_query = None
    
#     for natural_question, query in data:
#         match_count, matching_words = count_matching_words(input_question, natural_question)
#         if match_count > max_matches:
#             max_matches = match_count
#             best_natural_question = natural_question
#             best_query = query
    
#     return best_natural_question, best_query

# def log_token_frequencies(input_question, log_file_path):
#     """Log token frequencies from the input question to a file."""
#     tokens = input_question.lower().split()
#     token_frequencies = Counter(tokens)
    
#     # Write token frequencies to a log file, overwriting existing content
#     with open(log_file_path, mode='w', encoding='utf-8') as log_file:
#         for token, frequency in token_frequencies.items():
#             log_file.write(f"{token}: {frequency}\n")

# # Main program
# csv_file_path = 'nlp_sql_dataset.csv'  # Replace with your CSV file path
# log_file_path = 'token_frequencies.log'  # Log file to store token frequencies

# input_question = input("Please enter your question: ")

# # Log the token frequencies of the input question
# log_token_frequencies(input_question, log_file_path)

# # Find the best matching natural language question and SQL query
# best_natural_question, best_query = find_best_query(input_question, csv_file_path)

# if best_query:
#     print(f"Best matching natural language question: '{best_natural_question}'")
#     print(f"Corresponding SQL query: {best_query}")
# else:
#     print("No matching query found.")


import csv
import mysql.connector
from collections import Counter
import streamlit as st

def load_csv(file_path):
    """Load the CSV file and return a list of (question, query) tuples."""
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header if there's one
        return [(row[0], row[1]) for row in reader]

def count_matching_words(input_question, natural_question):
    """Count the number of matching words between two questions."""
    input_words = set(input_question.lower().split())
    natural_words = set(natural_question.lower().split())
    matching_words = input_words.intersection(natural_words)
    return len(matching_words), matching_words

def find_best_query(input_question, csv_file_path):
    """Find the SQL query with the maximum matching words for the input question."""
    data = load_csv(csv_file_path)
    
    max_matches = 0
    best_natural_question = None
    best_query = None
    
    for natural_question, query in data:
        match_count, matching_words = count_matching_words(input_question, natural_question)
        if match_count > max_matches:
            max_matches = match_count
            best_natural_question = natural_question
            best_query = query
    
    return best_natural_question, best_query

def log_token_frequencies(input_question, log_file_path):
    """Log token frequencies from the input question to a file."""
    tokens = input_question.lower().split()
    token_frequencies = Counter(tokens)
    
    with open(log_file_path, mode='w', encoding='utf-8') as log_file:
        for token, frequency in token_frequencies.items():
            log_file.write(f"{token}: {frequency}\n")

def execute_query(database_config, query):
    """Execute a SQL query on the MySQL database and return the results."""
    connection = None
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(**database_config)
        st.success("Successfully connected to the database.")
        
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()  # Fetch all results from the query
        
        return results
    except mysql.connector.Error as e:
        st.error(f"Database error: {e}")
        return None
    finally:
        if connection:
            cursor.close()
            connection.close()  # Close the connection
            st.info("Database connection closed.")

# Main Streamlit application
def main():
    st.title("Natural Language to SQL Query App")
    st.write("Ask your question below:")

    # CSV and log file paths
    csv_file_path = 'nlp_sql_dataset.csv'  # Replace with your CSV file path
    log_file_path = 'token_frequencies.log'  # Log file to store token frequencies

    # MySQL database configuration
    database_config = {
        'user': 'root',  # Replace with your MySQL username
        'password': 'Pass@1234',  # Replace with your MySQL password
        'host': 'localhost',  # Usually 'localhost' for local databases
        'database': 'wce4'  # Replace with your database name
    }

    input_question = st.text_input("Please enter your question:")

    if st.button("Submit"):
        if input_question:
            # Log the token frequencies of the input question
            log_token_frequencies(input_question, log_file_path)

            # Find the best matching natural language question and SQL query
            best_natural_question, best_query = find_best_query(input_question, csv_file_path)

            if best_query:
                st.write(f"**Best matching natural language question:** '{best_natural_question}'")
                st.write(f"**Corresponding SQL query:** `{best_query}`")
                
                # Execute the query on the MySQL database
                results = execute_query(database_config, best_query)
                
                if results is not None:
                    st.write("**Query Results:**")
                    for row in results:
                        st.write(row)
                else:
                    st.write("Failed to retrieve results from the database.")
            else:
                st.write("No matching query found.")
        else:
            st.warning("Please enter a question.")

if __name__ == "__main__":
    main()
