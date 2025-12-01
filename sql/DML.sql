-- Insert Members
INSERT INTO Member (first_name, last_name, email, phone, date_of_birth, registration_date) VALUES
('Adnan', 'Kazi', 'adnan.kazi@email.com', '613-555-0101', '1990-05-15', '2024-01-10'),
('Ahmer', 'Muhammad', 'ahmer.muhammad@email.com', '613-555-0102', '1988-08-22', '2024-02-15'),
('Umar', 'Marikar', 'umar.marikar@email.com', '613-555-0103', '1992-11-30', '2024-03-20'),
('Abdelghny', 'Orogat', 'abdelghny.orogat@email.com', '613-555-0104', '1995-03-12', '2024-04-05');


-- Insert User Credentials
INSERT INTO UserCredential (member_id, username, password_hash, last_login) VALUES
(1, 'adnan_kazi', '$2a$10$abcdefghijklmnopqrstuvwxyz123456', '2024-11-28 09:30:00'),
(2, 'ahmer_m', '$2a$10$bcdefghijklmnopqrstuvwxyz1234567', '2024-11-27 14:15:00'),
(3, 'umar_marikar', '$2a$10$cdefghijklmnopqrstuvwxyz12345678', '2024-11-28 08:45:00'),
(4, 'abdelghny_o', '$2a$10$defghijklmnopqrstuvwxyz123456789', '2024-11-26 18:20:00');


-- 3. Insert Trainers
INSERT INTO Trainer (first_name, last_name, email, phone, specialization) VALUES
('Jeff', 'Nippard', 'jeff.nippard@gymtrainer.com', '613-555-0201', 'Science-Based Bodybuilding & Powerlifting'),
('Chris', 'Bumstead', 'chris.bumstead@gymtrainer.com', '613-555-0202', 'Classic Physique & Bodybuilding'),
('Israel', 'Adesanya', 'israel.adesanya@gymtrainer.com', '613-555-0203', 'MMA Striking & Conditioning'),
('Khabib', 'Nurmagomedov', 'khabib.nurmagomedov@gymtrainer.com', '613-555-0204', 'Wrestling & Grappling');


-- Insert Group Classes
INSERT INTO GroupClass (class_name, description, duration, max_capacity, price) VALUES
('Morning Yoga Flow', 'Energizing yoga session to start your day', 60, 20, 25.00),
('HIIT Bootcamp', 'High-intensity interval training for maximum calorie burn', 45, 15, 30.00),
('Strength & Conditioning', 'Build muscle and improve overall strength', 60, 12, 35.00),
('Spin Class', 'Indoor cycling with energetic music and coaching', 45, 25, 28.00),
('Pilates Core', 'Focus on core strength and stability', 50, 18, 32.00);


-- Insert Rooms
INSERT INTO Room (room_name, capacity) VALUES
('Studio A', 25),
('Studio B', 30),
('Strength Room', 15),
('Cardio Zone', 20),
('Multipurpose Studio', 35);


-- Insert Facilities
INSERT INTO Facility (facility_name) VALUES
('Mirrors'),
('Sound System'),
('Yoga Mats'),
('Resistance Bands'),
('Spin Bikes'),
('Fans'),
('Water Station'),
('Weight Racks'),
('Barbells'),
('Dumbbells'),
('Benches'),
('Treadmills'),
('Ellipticals'),
('Rowing Machines'),
('Bikes'),
('Projector'),
('Mats'),
('Props');


-- Insert RoomFacility

-- Different Rooms and zones in the gym
INSERT INTO RoomFacility (room_id, facility_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4);

INSERT INTO RoomFacility (room_id, facility_id) VALUES
(2, 5), (2, 2), (2, 6), (2, 7);

INSERT INTO RoomFacility (room_id, facility_id) VALUES
(3, 8), (3, 9), (3, 10), (3, 11), (3, 1);

INSERT INTO RoomFacility (room_id, facility_id) VALUES
(4, 12), (4, 13), (4, 14), (4, 15);

INSERT INTO RoomFacility (room_id, facility_id) VALUES
(5, 2), (5, 16), (5, 17), (5, 18), (5, 1);


-- Insert Health History
INSERT INTO HealthHistory (member_id, weight, height, blood_pressure, record_date) VALUES
(1, 82.5, 175.0, '120/80', '2024-01-10'),
(1, 80.0, 175.0, '118/78', '2024-10-15'),
(2, 90.0, 180.5, '125/82', '2024-02-15'),
(2, 87.5, 180.5, '122/80', '2024-11-01'),
(3, 75.0, 172.0, '115/75', '2024-03-20'),
(3, 73.5, 172.0, '116/76', '2024-11-10'),
(4, 65.0, 165.0, '110/70', '2024-04-05');



-- Insert Sessions
INSERT INTO Session (class_id, room_id, trainer_id, schedule_time) VALUES

-- past sessions
(1, 1, 4, '2024-11-20 07:00:00'),
(2, 3, 1, '2024-11-21 18:00:00'),
(3, 3, 3, '2024-11-22 17:00:00'),

-- upcoming sessions
(1, 1, 4, '2024-11-30 07:00:00'),
(2, 3, 1, '2024-11-30 18:00:00'),
(3, 3, 3, '2024-12-01 17:00:00'),
(4, 2, 2, '2024-12-01 09:00:00'),
(5, 5, 3, '2024-12-02 19:00:00'),
(1, 1, 4, '2024-12-03 07:00:00'),
(2, 3, 1, '2024-12-03 18:00:00');


-- Insert Bookings
INSERT INTO Booking (member_id, session_id, booking_date, status) VALUES

-- past bookings
(1, 1, '2024-11-19 10:00:00', 'Attended'),
(2, 2, '2024-11-20 12:00:00', 'Attended'),
(3, 3, '2024-11-21 14:00:00', 'No-Show'),

-- upcoming bookings
(1, 4, '2024-11-25 09:00:00', 'Booked'),
(1, 6, '2024-11-26 10:00:00', 'Booked'),
(2, 5, '2024-11-26 11:00:00', 'Booked'),
(3, 7, '2024-11-27 08:00:00', 'Booked'),
(4, 8, '2024-11-27 09:00:00', 'Booked'),
(4, 5, '2024-11-28 08:00:00', 'Cancelled');


-- Insert Billing
INSERT INTO Billing (member_id, amount, billing_date, due_date, status, description) VALUES
(1, 150.00, '2024-01-10', '2024-01-31', 'Paid', 'Monthly Membership Fee - January'),
(1, 150.00, '2024-11-01', '2024-11-30', 'Paid', 'Monthly Membership Fee - November'),
(2, 150.00, '2024-02-15', '2024-03-15', 'Paid', 'Monthly Membership Fee - February'),
(2, 150.00, '2024-11-15', '2024-12-15', 'Pending', 'Monthly Membership Fee - November'),
(3, 150.00, '2024-03-20', '2024-04-20', 'Paid', 'Monthly Membership Fee - March'),
(3, 150.00, '2024-11-20', '2024-12-20', 'Pending', 'Monthly Membership Fee - November'),
(4, 150.00, '2024-04-05', '2024-05-05', 'Paid', 'Monthly Membership Fee - April'),
(4, 25.00, '2024-11-10', '2024-11-30', 'Overdue', 'Personal Training Session');



-- Insert Trainer Availability
INSERT INTO Availability (trainer_id, start_time, end_time) VALUES
(1, '2024-11-30 06:00:00', '2024-11-30 14:00:00'),
(1, '2024-12-01 06:00:00', '2024-12-01 14:00:00'),
(2, '2024-11-30 06:00:00', '2024-11-30 12:00:00'),
(2, '2024-12-01 14:00:00', '2024-12-01 20:00:00'),
(3, '2024-11-30 15:00:00', '2024-11-30 21:00:00'),
(3, '2024-12-01 15:00:00', '2024-12-01 21:00:00'),
(4, '2024-12-01 08:00:00', '2024-12-01 16:00:00');
