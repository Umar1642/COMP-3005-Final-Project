DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

CREATE TABLE Member (
    member_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    registration_date DATE DEFAULT CURRENT_DATE
);

CREATE TABLE UserCredential (
    credential_id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL UNIQUE, 
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    last_login TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES Member(member_id) ON DELETE CASCADE
);

CREATE TABLE Trainer (
    trainer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    specialization TEXT
);

CREATE TABLE GroupClass (
    class_id SERIAL PRIMARY KEY,
    price DECIMAL(10, 2) DEFAULT 0.00, 
    duration INTEGER NOT NULL,
    class_name VARCHAR(100) NOT NULL,
    description TEXT,
    max_capacity INTEGER NOT NULL
);

CREATE TABLE Room (
    room_id SERIAL PRIMARY KEY,
    room_name VARCHAR(50) NOT NULL,
    capacity INTEGER NOT NULL 
);

CREATE TABLE Facility (
    facility_id SERIAL PRIMARY KEY,
    facility_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE RoomFacility (
    room_id INTEGER NOT NULL,
    facility_id INTEGER NOT NULL,
    PRIMARY KEY (room_id, facility_id),
    FOREIGN KEY (room_id) REFERENCES Room(room_id) ON DELETE CASCADE,
    FOREIGN KEY (facility_id) REFERENCES Facility(facility_id) ON DELETE CASCADE
);

CREATE TABLE HealthHistory (
    health_history_id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL,
    weight DECIMAL(5, 2),
    height DECIMAL(5, 2),
    blood_pressure VARCHAR(20),
    record_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (member_id) REFERENCES Member(member_id) ON DELETE CASCADE
);

CREATE TABLE Session (
    session_id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    trainer_id INTEGER NOT NULL,
    schedule_time TIMESTAMP NOT NULL,
    FOREIGN KEY (class_id) REFERENCES GroupClass(class_id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES Room(room_id) ON DELETE RESTRICT,
    FOREIGN KEY (trainer_id) REFERENCES Trainer(trainer_id) ON DELETE RESTRICT
);

CREATE TABLE Booking (
    booking_id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL,
    session_id INTEGER NOT NULL,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Booked' CHECK (status IN ('Booked', 'Attended', 'Cancelled', 'No-Show')),
    FOREIGN KEY (member_id) REFERENCES Member(member_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES Session(session_id) ON DELETE CASCADE,
    UNIQUE(member_id, session_id) -- stops users from having more than 1 booking
);

CREATE TABLE Billing (
    billing_id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    billing_date DATE DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Paid', 'Overdue', 'Cancelled')),
    description TEXT,
    FOREIGN KEY (member_id) REFERENCES Member(member_id) ON DELETE CASCADE
);

CREATE TABLE Availability (
    availability_id SERIAL PRIMARY KEY,
    trainer_id INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    FOREIGN KEY (trainer_id) REFERENCES Trainer(trainer_id) ON DELETE CASCADE,
    CONSTRAINT valid_time_range CHECK (end_time > start_time)
);

-- our index
CREATE INDEX idx_session_scheduling ON Session(schedule_time, room_id, trainer_id);

-- our trigger
CREATE OR REPLACE FUNCTION check_member_availability()
RETURNS TRIGGER AS $$ 
BEGIN 
    -- checks if a member booked 2 sessions at the same time
    IF EXISTS (
        SELECT 1 
        FROM Booking b
        JOIN Session s ON b.session_id = s.session_id
        JOIN Session new_s ON NEW.session_id = new_s.session_id
        WHERE b.member_id = NEW.member_id
        AND b.status != 'Cancelled'
        AND s.session_id != new_s.session_id
        AND s.schedule_time = new_s.schedule_time 
    ) THEN
        RAISE EXCEPTION 'Member % is already booked in another session at the same time', NEW.member_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
 
CREATE TRIGGER prevent_double_booking
    BEFORE INSERT OR UPDATE ON Booking
    FOR EACH ROW
    EXECUTE FUNCTION check_member_availability();

-- the view 
CREATE VIEW MemberDashboard AS 
SELECT 
    m.member_id,
    m.first_name,
    m.last_name,
    m.email,
    m.phone,
    uc.username,
    uc.last_login,

    -- sees the most recent health metrics for a member
    (SELECT weight FROM HealthHistory WHERE member_id = m.member_id
    ORDER BY record_date DESC LIMIT 1) AS current_weight,

    -- counts the amount of upcoming booking for a member 
    (SELECT COUNT(*) FROM Booking b JOIN Session s ON b.session_id = s.session_id
    WHERE b.member_id = m.member_id AND b.status = 'Booked' AND s.schedule_time > CURRENT_TIMESTAMP) AS upcoming_sessions,

    -- any or all pending payments a member has
    (SELECT COUNT(*) FROM Billing WHERE member_id = m.member_id AND status = 'Pending')
    AS pending_payments,

    -- total amount of money spent by the member
    (SELECT COALESCE(SUM(amount), 0) FROM Billing WHERE member_id = m.member_id 
    AND status = 'Paid') AS total_spent,

    -- length a member has been a member with the gym
    (CURRENT_DATE - m.registration_date) AS membership_days

FROM Member m 
LEFT JOIN UserCredential uc ON m.member_id = uc.member_id
WHERE m.member_id IS NOT NULL;