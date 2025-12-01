import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta

# Database connection
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="Fitness_db", # Change to the name of your db
        user="postgres",
        password="postgres", # change to your password
        port = "5432"
    )

# member Functions

def register_member():
    """Function 1: User Registration"""
    print("\n=== MEMBER REGISTRATION ===")
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    email = input("Email: ")
    phone = input("Phone: ")
    dob = input("Date of Birth (YYYY-MM-DD): ")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Check duplicate email
        cur.execute("SELECT email FROM Member WHERE email = %s", (email,))
        if cur.fetchone():
            print("Error: Email already exists")
            return
        
        # Insert member
        cur.execute("""
            INSERT INTO Member (first_name, last_name, email, phone, date_of_birth)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING member_id
        """, (first_name, last_name, email, phone, dob))
        
        member_id = cur.fetchone()[0]
        conn.commit()
        print(f"Success Member ID: {member_id}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()


def log_health_history():
    """Function 2: Health History"""
    print("\n=== LOG HEALTH HISTORY ===")
    member_id = input("Member ID: ")
    weight = input("Weight (kg): ")
    height = input("Height (cm): ")
    blood_pressure = input("Blood Pressure (e.g., 120/80): ")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Validate member exists
        cur.execute("SELECT member_id FROM Member WHERE member_id = %s", (member_id,))
        if not cur.fetchone():
            print("Error: Member ID does not exist")
            return
        
        # Validate numeric values
        try:
            float(weight)
            float(height)
        except ValueError:
            print("Error: Weight and height must be numbers")
            return
            
        cur.execute("""
            INSERT INTO HealthHistory (member_id, weight, height, blood_pressure)
            VALUES (%s, %s, %s, %s)
            RETURNING health_history_id
        """, (member_id, weight, height, blood_pressure))
        
        history_id = cur.fetchone()[0]
        conn.commit()
        print(f"Health history logged Record ID: {history_id}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()


def schedule_pt_session():
    """Function 3: PT Session Scheduling"""
    print("\n=== SCHEDULE PERSONAL TRAINING SESSION ===")
    member_id = input("Member ID: ")
    trainer_id = input("Trainer ID: ")
    room_id = input("Room ID: ")
    session_date = input("Session Date & Time (YYYY-MM-DD HH:MM): ")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Validate IDs exist
        cur.execute("SELECT member_id FROM Member WHERE member_id = %s", (member_id,))
        if not cur.fetchone():
            print("Error: Member ID does not exist")
            return
            
        cur.execute("SELECT trainer_id FROM Trainer WHERE trainer_id = %s", (trainer_id,))
        if not cur.fetchone():
            print("Error: Trainer ID does not exist")
            return
            
        cur.execute("SELECT room_id FROM Room WHERE room_id = %s", (room_id,))
        if not cur.fetchone():
            print("Error: Room ID does not exist")
            return
        
        # Validate future date
        session_dt = datetime.strptime(session_date, '%Y-%m-%d %H:%M')
        if session_dt <= datetime.now():
            print("Error: Session must be scheduled for a future time")
            return
        
        # Create a simple session (using class_id = 1 as placeholder)
        cur.execute("""
            INSERT INTO Session (class_id, room_id, trainer_id, schedule_time)
            VALUES (1, %s, %s, %s)
            RETURNING session_id
        """, (room_id, trainer_id, session_date))
        
        session_id = cur.fetchone()[0]
        
        # Book the session for the member
        cur.execute("""
            INSERT INTO Booking (member_id, session_id, status)
            VALUES (%s, %s, 'Booked')
        """, (member_id, session_id))
        
        conn.commit()
        print(f"PT Session scheduled, Session ID: {session_id}")
        
    except ValueError:
        print("Error: Invalid date format. Use YYYY-MM-DD HH:MM")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()


def register_group_class():
    """Function 4: Group Class Registration"""
    print("\n=== REGISTER FOR GROUP CLASS ===")
    member_id = input("Member ID: ")
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Validate member exists
        cur.execute("SELECT member_id FROM Member WHERE member_id = %s", (member_id,))
        if not cur.fetchone():
            print("Error: Member ID does not exist")
            return
    
        cur.execute("""
            SELECT s.session_id, gc.class_name, s.schedule_time, r.room_name,
                   t.first_name || ' ' || t.last_name AS trainer
            FROM Session s
            JOIN GroupClass gc ON s.class_id = gc.class_id
            JOIN Room r ON s.room_id = r.room_id
            JOIN Trainer t ON s.trainer_id = t.trainer_id
            WHERE s.schedule_time > CURRENT_TIMESTAMP
            ORDER BY s.schedule_time
            LIMIT 10
        """)
        
        sessions = cur.fetchall()
        
        if not sessions:
            print("No upcoming classes available")
            cur.close()
            conn.close()
            return
        
        print("\n--- Available Classes ---")
        for sess in sessions:
            print(f"ID: {sess['session_id']} | {sess['class_name']} | {sess['schedule_time']} | {sess['room_name']} | Trainer: {sess['trainer']}")
        
        session_id = input("\nEnter Session ID to book: ")
        
        # Check if already registered
        cur.execute("SELECT * FROM Booking WHERE member_id = %s AND session_id = %s", (member_id, session_id))
        if cur.fetchone():
            print("Error: Already registered for this session")
            return
            
        # Check capacity
        cur.execute("""
            SELECT COUNT(*) as current_count, gc.max_capacity
            FROM Booking b
            JOIN Session s ON b.session_id = s.session_id
            JOIN GroupClass gc ON s.class_id = gc.class_id
            WHERE b.session_id = %s AND b.status = 'Booked'
            GROUP BY gc.max_capacity
        """, (session_id,))
        
        capacity_result = cur.fetchone()
        if capacity_result and capacity_result['current_count'] >= capacity_result['max_capacity']:
            print("Error: Class is full")
            return
        
        cur.execute("""
            INSERT INTO Booking (member_id, session_id, status)
            VALUES (%s, %s, 'Booked')
        """, (member_id, session_id))
        
        conn.commit()
        print(f"Successfully registered for class")
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()


# Trainere FUnction

def set_trainer_availability():
    """Function 5: Set Availability"""
    print("\n=== SET TRAINER AVAILABILITY ===")
    trainer_id = input("Trainer ID: ")
    start_time = input("Start Time (YYYY-MM-DD HH:MM): ")
    end_time = input("End Time (YYYY-MM-DD HH:MM): ")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Check for overlapping times
        cur.execute("""
            SELECT * FROM Availability
            WHERE trainer_id = %s
            AND (
                (start_time <= %s AND end_time > %s)
                OR (start_time < %s AND end_time >= %s)
                OR (start_time >= %s AND end_time <= %s)
            )
        """, (trainer_id, start_time, start_time, end_time, end_time, start_time, end_time))
        
        if cur.fetchone():
            print("Error: Overlapping time slot exists")
            return
        
        cur.execute("""
            INSERT INTO Availability (trainer_id, start_time, end_time)
            VALUES (%s, %s, %s)
            RETURNING availability_id
        """, (trainer_id, start_time, end_time))
        
        avail_id = cur.fetchone()[0]
        conn.commit()
        print(f"Availability set, ID: {avail_id}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()


def member_lookup():
    """Function 6: Member Lookup"""
    print("\n=== MEMBER LOOKUP ===")
    search = input("Search member name: ")
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT member_id, first_name, last_name, email, phone, date_of_birth
            FROM Member
            WHERE LOWER(first_name || ' ' || last_name) LIKE LOWER(%s)
        """, (f'%{search}%',))
        
        members = cur.fetchall()
        
        if not members:
            print("No members found")
            return
        
        print("\n--- Members Found ---")
        for m in members:
            print(f"ID: {m['member_id']} | {m['first_name']} {m['last_name']} | {m['email']} | {m['phone']}")
            
            # Show latest health history
            cur.execute("""
                SELECT weight, height, blood_pressure, record_date
                FROM HealthHistory
                WHERE member_id = %s
                ORDER BY record_date DESC
                LIMIT 1
            """, (m['member_id'],))
            
            health = cur.fetchone()
            if health:
                print(f"   Latest Health: {health['weight']}kg, {health['height']}cm, BP: {health['blood_pressure']} ({health['record_date']})")
            print()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()


def view_trainer_schedule():
    """Function 7: Schedule View"""
    print("\n=== TRAINER SCHEDULE ===")
    trainer_id = input("Trainer ID: ")
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get trainer info
        cur.execute("""
            SELECT first_name, last_name, specialization
            FROM Trainer
            WHERE trainer_id = %s
        """, (trainer_id,))
        
        trainer = cur.fetchone()
        if not trainer:
            print("Trainer not found")
            return
        
        print(f"\n--- Schedule for {trainer['first_name']} {trainer['last_name']} ---")
        print(f"Specialization: {trainer['specialization']}\n")
        
        # Get upcoming sessions
        cur.execute("""
            SELECT s.session_id, s.schedule_time, gc.class_name, r.room_name
            FROM Session s
            JOIN GroupClass gc ON s.class_id = gc.class_id
            JOIN Room r ON s.room_id = r.room_id
            WHERE s.trainer_id = %s
            AND s.schedule_time >= CURRENT_DATE
            AND s.schedule_time <= CURRENT_DATE + INTERVAL '7 days'
            ORDER BY s.schedule_time
        """, (trainer_id,))
        
        sessions = cur.fetchall()
        
        if sessions:
            print("Upcoming Sessions (Next 7 days):")
            for sess in sessions:
                print(f"  • {sess['schedule_time']} | {sess['class_name']} | Room: {sess['room_name']}")
        else:
            print("No upcoming sessions in the next 7 days.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()


# Admin Function

def book_room():
    """Function 8: Room Booking"""
    print("\n=== BOOK ROOM ===")
    room_id = input("Room ID: ")
    start_time = input("Start Time (YYYY-MM-DD HH:MM): ")
    end_time = input("End Time (YYYY-MM-DD HH:MM): ")
    purpose = input("Purpose: ")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Check if room exists
        cur.execute("SELECT room_id FROM Room WHERE room_id = %s", (room_id,))
        if not cur.fetchone():
            print("Error: Room ID does not exist")
            return
        
        # Check if room is already booked
        cur.execute("""
            SELECT * FROM Session
            WHERE room_id = %s
            AND schedule_time >= %s
            AND schedule_time < %s
        """, (room_id, start_time, end_time))
        
        if cur.fetchone():
            print("Error: Room already booked for this time")
            return
        
        print(f"   Room {room_id} is available for booking")
        print(f"   Time: {start_time} to {end_time}")
        print(f"   Purpose: {purpose}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()


def create_group_class():
    """Function 9: Create New Group Class"""
    print("\n=== CREATE GROUP CLASS ===")
    class_name = input("Class Name: ")
    description = input("Description: ")
    duration = input("Duration (minutes): ")
    max_capacity = input("Max Capacity: ")
    price = input("Price: ")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Validate numeric inputs
        try:
            int(duration)
            int(max_capacity)
            float(price)
        except ValueError:
            print("Error: Duration and capacity must be integers, price must be a number")
            return
            
        # Check for duplicate class name
        cur.execute("SELECT class_id FROM GroupClass WHERE class_name = %s", (class_name,))
        if cur.fetchone():
            print("Error: Class name already exists")
            return
        
        cur.execute("""
            INSERT INTO GroupClass (class_name, description, duration, max_capacity, price)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING class_id
        """, (class_name, description, duration, max_capacity, price))
        
        class_id = cur.fetchone()[0]
        conn.commit()
        print(f"Group class created, Class ID: {class_id}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()


def assign_class_to_session():
    """Function 10: Assign Class to Room & Trainer"""
    print("\n=== ASSIGN CLASS TO SESSION ===")
    class_id = input("Class ID: ")
    trainer_id = input("Trainer ID: ")
    room_id = input("Room ID: ")
    schedule_time = input("Schedule Time (YYYY-MM-DD HH:MM): ")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Validate IDs exist
        cur.execute("SELECT class_id FROM GroupClass WHERE class_id = %s", (class_id,))
        if not cur.fetchone():
            print("Error: Class ID does not exist")
            return
            
        cur.execute("SELECT trainer_id FROM Trainer WHERE trainer_id = %s", (trainer_id,))
        if not cur.fetchone():
            print("Error: Trainer ID does not exist")
            return
            
        cur.execute("SELECT room_id FROM Room WHERE room_id = %s", (room_id,))
        if not cur.fetchone():
            print("Error: Room ID does not exist")
            return
        
        # Validate future date
        session_dt = datetime.strptime(schedule_time, '%Y-%m-%d %H:%M')
        if session_dt <= datetime.now():
            print("Error: Session must be scheduled for a future time")
            return
        
        # Check room availability
        cur.execute("""
            SELECT * FROM Session 
            WHERE room_id = %s AND schedule_time = %s
        """, (room_id, schedule_time))
        if cur.fetchone():
            print("Error: Room already booked at this time")
            return
        
        cur.execute("""
            INSERT INTO Session (class_id, room_id, trainer_id, schedule_time)
            VALUES (%s, %s, %s, %s)
            RETURNING session_id
        """, (class_id, room_id, trainer_id, schedule_time))
        
        session_id = cur.fetchone()[0]
        conn.commit()
        print(f"Session created, Session ID: {session_id}")
        
    except ValueError:
        print("Error: Invalid date format. Use YYYY-MM-DD HH:MM")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()


def generate_bill():
    """Function 11: Generate Bill"""
    print("\n=== GENERATE BILL ===")
    member_id = input("Member ID: ")
    amount = input("Amount: ")
    description = input("Description: ")
    due_date = input("Due Date (YYYY-MM-DD): ")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Validate member exists
        cur.execute("SELECT member_id FROM Member WHERE member_id = %s", (member_id,))
        if not cur.fetchone():
            print("Error: Member ID does not exist")
            return
            
        # Validate amount
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                print("Error: Amount must be positive")
                return
        except ValueError:
            print("Error: Amount must be a number")
            return
        
        cur.execute("""
            INSERT INTO Billing (member_id, amount, due_date, description, status)
            VALUES (%s, %s, %s, %s, 'Pending')
            RETURNING billing_id
        """, (member_id, amount, due_date, description))
        
        billing_id = cur.fetchone()[0]
        conn.commit()
        print(f"   Bill generated, Billing ID: {billing_id}")
        print(f"   Amount: ${amount}")
        print(f"   Status: Pending")
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()


def process_payment():
    """Function 12: Process Payment"""
    print("\n=== PROCESS PAYMENT ===")
    billing_id = input("Billing ID: ")
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Show bill details
        cur.execute("""
            SELECT b.billing_id, b.amount, b.status, b.description,
                   m.first_name, m.last_name
            FROM Billing b
            JOIN Member m ON b.member_id = m.member_id
            WHERE b.billing_id = %s
        """, (billing_id,))
        
        bill = cur.fetchone()
        
        if not bill:
            print("Bill not found")
            return
        
        print(f"\n--- Bill Details ---")
        print(f"Member: {bill['first_name']} {bill['last_name']}")
        print(f"Amount: ${bill['amount']}")
        print(f"Description: {bill['description']}")
        print(f"Current Status: {bill['status']}")
        
        if bill['status'] == 'Paid':
            print("\nThis bill is already paid")
            return
        
        confirm = input("\nProcess payment? (yes/no): ")
        
        if confirm.lower() == 'yes':
            cur.execute("""
                UPDATE Billing
                SET status = 'Paid'
                WHERE billing_id = %s
            """, (billing_id,))
            
            conn.commit()
            print("Payment processed successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

# CLI

def member_menu():
    """Member-only menu"""
    while True:
        print("\n" + "-"*50)
        print("   Health and Fitness Club Management System - MEMBER PORTAL")
        print("-"*50)
        print("\n MEMBER FUNCTIONS:")
        print("  1. User Registration")
        print("  2. Log Health History")
        print("  3. Schedule PT Session")
        print("  4. Register for Group Class")
        print("\n  0. Logout")
        print("-"*50)
        
        choice = input("\nSelect option: ")
        
        if choice == "1":
            register_member()
        elif choice == "2":
            log_health_history()
        elif choice == "3":
            schedule_pt_session()
        elif choice == "4":
            register_group_class()
        elif choice == "0":
            print("\nLogging out...")
            break
        else:
            print("\nInvalid option")
        
        input("\nPress Enter to continue...")


def trainer_menu():
    """Trainer-only menu"""
    while True:
        print("\n" + "-"*50)
        print("   Health and Fitness Club Management System - TRAINER PORTAL")
        print("-"*50)
        print("\n TRAINER FUNCTIONS:")
        print("  1. Set Availability")
        print("  2. Member Lookup")
        print("  3. View My Schedule")
        print("\n  0. Logout")
        print("-"*50)
        
        choice = input("\nSelect option: ")
        
        if choice == "1":
            set_trainer_availability()
        elif choice == "2":
            member_lookup()
        elif choice == "3":
            view_trainer_schedule()
        elif choice == "0":
            print("\nLogging out...")
            break
        else:
            print("\nInvalid option")
        
        input("\nPress Enter to continue...")


def admin_menu():
    """Admin-only menu"""
    while True:
        print("\n" + "-"*50)
        print("   Health and Fitness Club Management System - ADMIN PORTAL")
        print("-"*50)
        print("\n ADMIN FUNCTIONS:")
        print("  1. Book Room")
        print("  2. Create Group Class")
        print(" 3. Assign Class to Session")
        print(" 4. Generate Bill")
        print(" 5. Process Payment")
        print("\n  0. Logout")
        print("-"*50)
        
        choice = input("\nSelect option: ")
        
        if choice == "1":
            book_room()
        elif choice == "2":
            create_group_class()
        elif choice == "3":
            assign_class_to_session()
        elif choice == "4":
            generate_bill()
        elif choice == "5":
            process_payment()
        elif choice == "0":
            print("\nLogging out...")
            break
        else:
            print("\nInvalid option")
        
        input("\nPress Enter to continue...")


def role_selection():
    """Initial role selection menu"""
    while True:
        print("\n" + "-"*50)
        print("  GYM MANAGEMENT SYSTEM")
        print("-"*50)
        print("\n SELECT YOUR ROLE:")
        print("  1. Member")
        print("  2. Trainer")
        print("  3. Admin")
        print("  0. Exit")
        print("-"*50)
        
        choice = input("\nSelect option: ")
        
        if choice == "1":
            member_menu()
        elif choice == "2":
            trainer_menu()
        elif choice == "3":
            admin_menu()
        elif choice == "0":
            print("\nClosing...")
            break
        else:
            print("\nInvalid option")


if __name__ == "__main__":
    try:
        role_selection()
    except KeyboardInterrupt:
        print("\n\nClosing")
    except Exception as e:
        print(f"\nError: {e}")
