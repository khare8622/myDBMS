import os
import re
import json
import shutil

current_db = None

def create_db(db_name):
    if not os.path.exists(db_name):
        os.makedirs(db_name)
        print(f"Database {db_name} created.")
    else:
        print(f"Database {db_name} already exists.")

def use_db(db_name):
    global current_db
    if os.path.exists(db_name):
        current_db = db_name
        print(f"Using database {db_name}.")
    else:
        print(f"Database {db_name} not found.")

def create_table(table_name, columns):
    if current_db:
        table_path = os.path.join(current_db, f"{table_name}.json")
        if not os.path.exists(table_path):
            # Check if a primary key is defined
            primary_key = None
            parsed_columns = []
            for column in columns:
                column_parts = column.strip().split()
                
                if len(column_parts) == 3 and column_parts[2].lower() == "primary":
                    if primary_key:
                        print("Error: Only one primary key is allowed.")
                        return
                    primary_key = column_parts[0]
                    parsed_columns.append({"name": column_parts[0], "type": column_parts[1], "primary": True})
                elif len(column_parts) == 2:
                    parsed_columns.append({"name": column_parts[0], "type": column_parts[1], "primary": False})
                else:
                    print("Error: Invalid column definition.")
                    return
            
            if not primary_key:
                print("Error: A table must have one primary key.")
                return

            # Create table structure
            table_structure = {"columns": parsed_columns, "rows": [], "primary_key": primary_key}
            with open(table_path, 'w') as table_file:
                json.dump(table_structure, table_file, indent=4)  # Pretty print for readability
            print(f"Table {table_name} created with primary key {primary_key}.")
        else:
            print(f"Table {table_name} already exists.")
    else:
        print("No database selected. Use 'USE db_name' first.")


def insert_into_table(table_name, values):
    if current_db:
        table_path = os.path.join(current_db, f"{table_name}.json")
        if os.path.exists(table_path):
            with open(table_path, 'r') as table_file:
                table_structure = json.load(table_file)
            
            # Extract column details and primary key
            columns = table_structure["columns"]
            primary_key = table_structure["primary_key"]
            primary_key_index = next((i for i, col in enumerate(columns) if col["name"] == primary_key), -1)
            
            if primary_key_index == -1:
                print("Error: Primary key not found in table structure.")
                return
            
            # Check if the number of values matches the columns
            if len(values) != len(columns):
                print("Error: Value count does not match column count.")
                return
            
            # Validate primary key uniqueness
            for row in table_structure["rows"]:
                if row[primary_key_index] == values[primary_key_index]:
                    print(f"Error: Duplicate value for primary key {primary_key}.")
                    return
            
            # Insert the new row
            table_structure["rows"].append(values)
            with open(table_path, 'w') as table_file:
                json.dump(table_structure, table_file)
            print(f"Data inserted into {table_name}.")
        else:
            print(f"Table {table_name} not found.")
    else:
        print("No database selected. Use 'USE db_name' first.")

def show_tables():
    if current_db:
        # List all .json files in the current database folder
        tables = [f.split(".")[0] for f in os.listdir(current_db) if f.endswith(".json")]
        if tables:
            print("Tables:")
            for table in tables:
                print(f"- {table}")
        else:
            print("No tables found in the current database.")
    else:
        print("No database selected. Use 'USE db_name' first.")


def select_from_table(table_name, columns="*", where_condition=None):
    if current_db:
        table_path = os.path.join(current_db, f"{table_name}.json")
        if os.path.exists(table_path):
            with open(table_path, 'r') as table_file:
                table_data = json.load(table_file)
            
            # Extract column names from table data
            column_names = [column["name"].lower() for column in table_data["columns"]]
            
            # If the user selected '*' (all columns), then we select all columns
            if columns == "*":
                selected_columns = column_names
            elif columns:
                # Otherwise, process the columns passed in the query
                selected_columns = columns.split(",")  # Handle column selection like 'id,name'
                selected_columns = [col.strip().lower() for col in selected_columns]  # Strip extra spaces and lowercase

                # Check if all selected columns exist in the table
                invalid_columns = [col for col in selected_columns if col not in column_names]
                if invalid_columns:
                    print(f"Error: Invalid column(s): {', '.join(invalid_columns)}")
                    return
            else:
                # If no columns are passed, we show all columns by default
                selected_columns = column_names
            
            # Get the maximum length for each column, including column names
            column_lengths = {col: len(col) for col in selected_columns}  # Start with column name lengths

            # Find the max length of data for each selected column
            for row in table_data["rows"]:
                for idx, col in enumerate(selected_columns):
                    column_idx = column_names.index(col)
                    column_lengths[col] = max(column_lengths[col], len(str(row[column_idx])))
            
            # Print the column headers with proper formatting
            header = " | ".join([col.ljust(column_lengths[col]) for col in selected_columns])
            print(f"+{'-' * (len(header) - 2)}+")
            print(f"| {header} |")
            print(f"+{'-' * (len(header) - 2)}+")
            
            # Apply WHERE condition if provided
            filtered_rows = table_data["rows"]
            if where_condition:
                # Parse the WHERE condition
                condition_column, condition_value = where_condition
                condition_column = condition_column.strip().lower()
                
                # Check if the column exists
                if condition_column not in column_names:
                    print(f"Error: Column {condition_column} not found.")
                    return
                
                # Find the column's data type
                column_data_type = next((col["type"] for col in table_data["columns"] if col["name"].lower() == condition_column), None)
                
                # If condition value is numeric, convert to appropriate type
                if column_data_type == "int" or column_data_type == "float":
                    try:
                        condition_value = float(condition_value)
                    except ValueError:
                        print(f"Error: Invalid value for column {condition_column}. Expected type {column_data_type}.")
                        return
                
                # Filter rows based on where condition
                filtered_rows = [row for row in table_data["rows"] 
                                 if str(row[column_names.index(condition_column)]).strip().lower() == str(condition_value).strip().lower()]
            
            # Print the rows with proper alignment
            if filtered_rows:
                for row in filtered_rows:
                    row_data = " | ".join([str(row[column_names.index(col)]).ljust(column_lengths[col]) for col in selected_columns])
                    print(f"| {row_data} |")
                print(f"+{'-' * (len(header) - 2)}+")
            else:
                print(f"Table {table_name} with {condition_column} = {condition_value} not found.")
        else:
            print(f"Table {table_name} not found.")
    else:
        print("No database selected. Use 'USE db_name' first.")





def update_table(table_name, updates, where_condition):
    if current_db:
        table_path = os.path.join(current_db, f"{table_name}.json")
        if os.path.exists(table_path):
            with open(table_path, 'r') as table_file:
                table_data = json.load(table_file)

            # Parse updates and WHERE clause
            update_pairs = updates.split(",")
            update_dict = {}
            for pair in update_pairs:
                key, value = pair.strip().split("=")
                update_dict[key.strip()] = value.strip().strip("'")

            where_key, where_value = where_condition.split("=")
            where_key = where_key.strip()
            where_value = where_value.strip().strip("'")

            # Create a column-to-index mapping
            column_indices = {col["name"]: idx for idx, col in enumerate(table_data["columns"])}

            updated_rows = 0
            for row in table_data["rows"]:
                # Map row values to column names
                row_dict = {col["name"]: row[idx] for idx, col in enumerate(table_data["columns"])}

                if str(row_dict.get(where_key)) == where_value:
                    # Apply updates to the row using column indices
                    for key, value in update_dict.items():
                        if key in column_indices:
                            row[column_indices[key]] = value
                    updated_rows += 1

            if updated_rows > 0:
                with open(table_path, 'w') as table_file:
                    json.dump(table_data, table_file)
                print(f"{updated_rows} row(s) updated successfully in {table_name}.")
            else:
                print(f"No rows matched the condition in {table_name}.")
        else:
            print(f"Table {table_name} not found.")
    else:
        print("No database selected. Use 'USE db_name' first.")


def delete_from_table(table_name, where_condition=None):
    if current_db:
        table_path = os.path.join(current_db, f"{table_name}.json")
        if os.path.exists(table_path):
            with open(table_path, 'r') as table_file:
                table_data = json.load(table_file)

            # If no WHERE clause, delete all rows
            if where_condition is None:
                confirm = input(f"Are you sure you want to delete all rows from {table_name}? (yes/no): ").strip().lower()
                if confirm == "yes":
                    table_data["rows"] = []
                    print(f"All rows deleted from {table_name}.")
                else:
                    print("Deletion aborted.")
                    return
            else:
                # Parse WHERE clause
                where_parts = where_condition.split("=")
                if len(where_parts) != 2:
                    print("Error: Invalid WHERE clause. Use 'column = value'.")
                    return
                where_column = where_parts[0].strip()
                where_value = where_parts[1].strip()

                # Validate the column in WHERE clause
                column_names = [col["name"] for col in table_data["columns"]]
                if where_column not in column_names:
                    print(f"Error: Column '{where_column}' does not exist in table '{table_name}'.")
                    return

                # Get the index of the column to apply the condition
                column_index = column_names.index(where_column)
                original_row_count = len(table_data["rows"])

                # Filter rows that do not match the WHERE condition
                table_data["rows"] = [
                    row for row in table_data["rows"] if str(row[column_index]) != where_value
                ]

                deleted_count = original_row_count - len(table_data["rows"])
                if deleted_count > 0:
                    print(f"{deleted_count} row(s) deleted from {table_name}.")
                else:
                    print("No rows matched the condition.")

            # Save updated table data
            with open(table_path, 'w') as table_file:
                json.dump(table_data, table_file)
        else:
            print(f"Table {table_name} not found.")
    else:
        print("No database selected. Use 'USE db_name' first.")


def delete_table(table_name):
    if current_db:
        table_path = os.path.join(current_db, f"{table_name}.json")
        if os.path.exists(table_path):
            os.remove(table_path)
            print(f"Table {table_name} deleted successfully.")
        else:
            print(f"Error: Table {table_name} does not exist in the database.")
    else:
        print("Error: No database selected. Use 'USE db_name' first.")

current_db = None
def drop_db(db_name):
    global current_db  # Declare global only when modifying current_db
    
    if current_db == db_name:
        current_db = None  # Reset current_db if it's the one being dropped
    
    db_path = os.path.join(os.getcwd(), db_name)
    if os.path.exists(db_path):
        confirm = input(f"Are you sure you want to delete the database {db_name}? (yes/no): ").strip().lower()
        if confirm == "yes":
            shutil.rmtree(db_path)  # Delete the entire database folder and its contents
            print(f"Database {db_name} deleted successfully.")
        else:
            print("Database deletion aborted.")
    else:
        print(f"Error: Database {db_name} does not exist.")



def main():
    print("Welcome to the MySQL")
    print("Created by- Shubh")
    while True:
        command = input("> ").strip().rstrip(";")  # Remove semicolon if present
        if command.lower() == "exit":
            print("Exiting the DBMS. Goodbye!")
            break
        elif command.lower().startswith("create database"):
            try:
                _, _, db_name = command.split(maxsplit=2)
                create_db(db_name)
            except ValueError:
                print("Syntax Error: CREATE DATABASE db_name;")
        elif command.lower().startswith("use"):
            try:
                _, db_name = command.split(maxsplit=1)
                use_db(db_name)
            except ValueError:
                print("Syntax Error: USE db_name;")
        elif command.lower().startswith("create table"):
            try:
                table_name = command.split("(")[0].split()[-1]
                columns_str = command.split("(")[1].rstrip(")")
                columns = [col.strip() for col in columns_str.split(",")]
                create_table(table_name, columns)
            except (IndexError, ValueError):
                print("Syntax Error: CREATE TABLE table_name (column1 datatype PRIMARY, column2 datatype, ...);")
        elif command.lower().startswith("insert into"):
            try:
                # Extract table name and values using regex
                match = re.match(r"insert into (\w+) values\s*\((.+)\)", command, re.IGNORECASE)
                if match:
                    table_name = match.group(1)
                    values_str = match.group(2)
                    # Split values, handling quotes properly
                    values = re.findall(r"(?:'([^']*)'|\"([^\"]*)\"|([^,]+))", values_str)
                    values = [v[0] or v[1] or v[2].strip() for v in values]  # Pick the matched group
                    insert_into_table(table_name, values)
                else:
                    print("Syntax Error: INSERT INTO table_name VALUES (value1, value2, ...);")
            except Exception as e:
                print(f"Error: {e}")
        elif command.lower() == "show tables":
            show_tables()
        elif command.lower().startswith("select"):
            try:
                # Split command into SELECT and FROM parts
                parts = command.lower().split("from", maxsplit=1)
                if len(parts) != 2:
                    raise ValueError("Syntax Error")
                
                columns = parts[0].replace("select", "").strip()
                table_name = parts[1].strip()
                
                # Handle the SELECT function
                if not table_name:
                    raise ValueError("Syntax Error")
                select_from_table(table_name, columns)
            except (IndexError, ValueError, SyntaxError):
                print("Syntax Error: SELECT column1, column2 FROM table_name; or SELECT * FROM table_name;")
        elif command.lower().startswith("update"):
            if "set" not in command.lower() or "where" not in command.lower():
                print("Syntax Error: UPDATE table_name SET column1 = value1, column2 = value2 WHERE column = value;")
            else:
                try:
                    # Parse the command into table name, SET, and WHERE clauses
                    update_parts = command.lower().split("set", maxsplit=1)
                    table_name = update_parts[0].replace("update", "").strip()
                    
                    set_and_where = update_parts[1].split("where", maxsplit=1)
                    updates = set_and_where[0].strip()
                    where_condition = set_and_where[1].strip()
                    
                    # Call the update_table function
                    update_table(table_name, updates, where_condition)
                except IndexError:
                    print("Syntax Error: UPDATE table_name SET column1 = value1, column2 = value2 WHERE column = value;")
        elif command.startswith("DELETE FROM"):
            parts = command.split("WHERE", maxsplit=1)
            table_name = parts[0].replace("DELETE FROM", "").strip()
            where_condition = parts[1].strip() if len(parts) > 1 else None
            delete_from_table(table_name, where_condition)
        elif command.lower().startswith("delete table"):
            try:
                table_name = command.split()[-1]
                delete_table(table_name)
            except IndexError:
                print("Syntax Error: DELETE TABLE table_name;")
        elif command.lower().startswith("drop database"):
            try:
                _, _, db_name = command.split(maxsplit=2)
                drop_db(db_name)
            except ValueError:
                print("Syntax Error: DROP DATABASE db_name;")

        else:
            print("Unknown command or syntax error. Please try again.")

if __name__ == "__main__":
    main()
