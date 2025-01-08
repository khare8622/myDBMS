# Custom DBMS Project

This is a custom-built Database Management System (DBMS) implemented in Python. It mimics basic functionalities of MySQL, including support for commands like `CREATE DB`, `USE`, `CREATE TABLE`, `INSERT INTO`, `SELECT`, `DELETE`, and more. The project is designed to offer a simplified version of MySQL functionalities with some additional custom features.

---

## Features

### Database Operations
- **CREATE DB `<dbname>`**: Creates a new database folder.
- **USE `<dbname>`**: Selects a database for subsequent operations.

### Table Operations
- **CREATE TABLE `<table_name>` (`column1 datatype PRIMARY KEY AUTO_INCREMENT`, `column2 datatype`, ...)**:
  - Creates a table within the selected database.
  - Supports `PRIMARY KEY` and `AUTO_INCREMENT`.
- **DROP TABLE `<table_name>`**: Deletes a table from the database.
- **DELETE FROM `<table_name>`**: Deletes all rows or specific rows based on conditions.
- **SELECT**:
  - `SELECT * FROM <table_name>`: Displays all rows in a formatted table.
  - `SELECT * FROM <table_name> WHERE <column> = <value>`: Filters rows based on a condition.

### Data Manipulation
- **INSERT INTO `<table_name>` VALUES (`value1`, `value2`, ...)**: Inserts a new row into the table.

---

## Getting Started

### Prerequisites
- Python 3.x
- JSON library (standard in Python)
- File handling for local storage

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/khare8622/myDBMS.git
   ```
2. Navigate to the project directory:
   ```bash
   cd myDBMS
   ```
3. Run the script:
   ```bash
   python main.py
   ```

---

## Commands Syntax

### Database Commands
- `CREATE DB <dbname>`: Creates a new database.
- `USE <dbname>`: Switches to the specified database.

### Table Commands
- `CREATE TABLE <table_name> (<column_name> <datatype> PRIMARY KEY AUTO_INCREMENT, ...)`
- `DROP TABLE <table_name>`

### Data Manipulation Commands
- `INSERT INTO <table_name> VALUES (<value1>, <value2>, ...)`
- `SELECT * FROM <table_name>`
- `SELECT * FROM <table_name> WHERE <column> = <value>`
- `DELETE FROM <table_name>`
- `DELETE FROM <table_name> WHERE <column> = <value>`

---

## Example Usage

```sql
> CREATE DB mydb
Database mydb created.

> USE mydb
Using database mydb.

> CREATE TABLE employees (id int PRIMARY KEY AUTO_INCREMENT, name string, post string, age int)
Table employees created.

> INSERT INTO employees VALUES (NULL, 'Shubh Khare', 'Software Engineer', 19)
Data inserted into employees.

> SELECT * FROM employees
+-----+------------+--------------------+-----+
| id  | name       | post               | age |
+-----+------------+--------------------+-----+
| 101 | Shubh Khare| Software Engineer | 19  |
+-----+------------+--------------------+-----+

> DELETE FROM employees WHERE id = 101
Row deleted successfully.
```

---

## Project Structure

- `main.py`: The main script that runs the DBMS.
- `databases/`: Directory where all databases and their tables are stored as JSON files.

---

## Limitations
- Does not support complex SQL queries.
- No concurrent access or transaction support.
- Limited data validation.

---

## Future Enhancements
- Add support for JOIN operations.
- Implement better error handling and logging.
- Add a GUI for easier interaction.

---

## License
This project is licensed under the MIT License. See the LICENSE file for details.

---

## Authors
- **Shubh Khare** - Developer
