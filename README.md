COMP3005 Final Project
Adnan Kazi | Member 1 101304031
Umar Marikar | Member 2 101310164
Ahmer Muhammad | Member 3 101312213


Steps to compile and run application:
1. Download app.py, ddl.sql, and dml.sql files. 
2. If python 3.7 or higher is not installed already, install it from python.org
3. If PostgreSQL 12 or higher is not installed already, install it from postgresql.org
4. If psycopg2 library is not installed already, install it by opening the command line/terminal and running this command: pip3 install psycopg2
5. Open pgAdmin
6. Create a new database named Fitness_db by: right-clicking "Databases" > "Create" > "Database" > name it "Fitness_db"
7. Open Query Tool by right-clicking "Databases" > "Query Tool"
8. Click the folder icon and open the ddl.sql and dml.sql files
9. Click the Execute button to verify that the data is inserted
10. Open app.py, go to line 11 and change the password to your actual PostgreSQL password
11. If not done already open the terminal and change the directory to where app.py is located
12. Run the application by entering this: python3 app.py
13. Now you can use the menu to perform operations


Implemented Functions:

Member:
User registration
Health history
PT session scheduling
Group class registration

Trainer:
Set availability
Member lookup
Schedule View

Administrative Staff:
Billing & Payment
Class Management
Room Booking


Video Link:
https://youtu.be/OSHIrgXGDws
