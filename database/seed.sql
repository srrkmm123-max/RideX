-- ============================================================
-- RideX Development / Test Seed Data
-- File: database/seed.sql
-- ============================================================

BEGIN;


-- ============================================================
-- 1. USERS
-- ============================================================

INSERT INTO users (
    user_id,
    first_name,
    last_name,
    email,
    phone,
    password_hash,
    role,
    status
)
VALUES

(
    '00000000-0000-0000-0000-000000000001',
    'Ranga',
    'Passenger',
    'passenger1@ridex.example',
    '+910000000001',
    'DEMO_PASSWORD_HASH',
    'passenger',
    'active'
),

(
    '00000000-0000-0000-0000-000000000002',
    'Suresh',
    'Driver',
    'driver1@ridex.example',
    '+910000000002',
    'DEMO_PASSWORD_HASH',
    'driver',
    'active'
),

(
    '00000000-0000-0000-0000-000000000003',
    'Raj',
    'Driver',
    'driver2@ridex.example',
    '+910000000003',
    'DEMO_PASSWORD_HASH',
    'driver',
    'active'
),

(
    '00000000-0000-0000-0000-000000000004',
    'Anita',
    'Passenger',
    'passenger2@ridex.example',
    '+910000000004',
    'DEMO_PASSWORD_HASH',
    'passenger',
    'active'
),

(
    '00000000-0000-0000-0000-000000000005',
    'RideX',
    'Administrator',
    'admin@ridex.example',
    '+910000000005',
    'DEMO_PASSWORD_HASH',
    'admin',
    'active'
)

ON CONFLICT (user_id) DO NOTHING;


-- ============================================================
-- 2. VEHICLES
-- ============================================================

INSERT INTO vehicles (
    vehicle_id,
    driver_id,
    vehicle_number,
    make,
    model,
    year,
    color,
    vehicle_type,
    capacity,
    status
)
VALUES

(
    '10000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000002',
    'TS09AB1234',
    'Maruti Suzuki',
    'Swift',
    2024,
    'White',
    'car',
    4,
    'active'
),

(
    '10000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000003',
    'TS10XY5678',
    'Hyundai',
    'i20',
    2023,
    'Silver',
    'car',
    4,
    'active'
)

ON CONFLICT (vehicle_id) DO NOTHING;


-- ============================================================
-- 3. DRIVER PROFILES
-- ============================================================

INSERT INTO drivers (
    driver_id,
    license_number,
    license_expiry,
    vehicle_id,
    driver_status,
    verification_status,
    current_latitude,
    current_longitude,
    current_heading,
    current_speed_kmph,
    last_location_update,
    total_rides,
    total_earnings,
    average_rating
)
VALUES

(
    '00000000-0000-0000-0000-000000000002',
    'DL-DEMO-0001',
    '2030-12-31',
    '10000000-0000-0000-0000-000000000001',
    'online',
    'verified',
    17.3850,
    78.4867,
    90,
    25,
    NOW(),
    125,
    45000.00,
    4.80
),

(
    '00000000-0000-0000-0000-000000000003',
    'DL-DEMO-0002',
    '2031-06-30',
    '10000000-0000-0000-0000-000000000002',
    'online',
    'verified',
    17.3900,
    78.4900,
    180,
    20,
    NOW(),
    98,
    36000.00,
    4.65
)

ON CONFLICT (driver_id) DO NOTHING;


-- ============================================================
-- 4. EMERGENCY CONTACTS
-- ============================================================

INSERT INTO emergency_contacts (
    contact_id,
    user_id,
    contact_name,
    phone,
    relationship,
    is_primary
)
VALUES

(
    '20000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    'Demo Emergency Contact',
    '+910000000010',
    'family',
    TRUE
),

(
    '20000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000004',
    'Demo Emergency Contact',
    '+910000000011',
    'family',
    TRUE
)

ON CONFLICT (contact_id) DO NOTHING;


-- ============================================================
-- 5. SAMPLE COMPLETED RIDE
-- ============================================================

INSERT INTO rides (
    ride_id,
    passenger_id,
    driver_id,
    vehicle_id,

    pickup_address,
    pickup_latitude,
    pickup_longitude,

    destination_address,
    destination_latitude,
    destination_longitude,

    estimated_distance_km,
    estimated_duration_minutes,

    actual_distance_km,
    actual_duration_minutes,

    estimated_fare,
    final_fare,

    surge_multiplier,

    payment_status,
    ride_status,

    requested_at,
    accepted_at,
    started_at,
    completed_at
)
VALUES
(
    '30000000-0000-0000-0000-000000000001',

    '00000000-0000-0000-0000-000000000001',

    '00000000-0000-0000-0000-000000000002',

    '10000000-0000-0000-0000-000000000001',

    'HITEC City, Hyderabad',
    17.4483,
    78.3915,

    'Secunderabad Railway Station',
    17.4399,
    78.4983,

    14.20,
    35,

    14.50,
    38,

    320.00,
    335.00,

    1.00,

    'paid',
    'completed',

    NOW() - INTERVAL '2 hours',
    NOW() - INTERVAL '115 minutes',
    NOW() - INTERVAL '105 minutes',
    NOW() - INTERVAL '67 minutes'
)

ON CONFLICT (ride_id) DO NOTHING;


-- ============================================================
-- 6. SAMPLE ACTIVE RIDE
-- ============================================================

INSERT INTO rides (
    ride_id,
    passenger_id,
    driver_id,
    vehicle_id,

    pickup_address,
    pickup_latitude,
    pickup_longitude,

    destination_address,
    destination_latitude,
    destination_longitude,

    estimated_distance_km,
    estimated_duration_minutes,

    estimated_fare,

    surge_multiplier,

    payment_status,
    ride_status,

    requested_at,
    accepted_at
)
VALUES
(
    '30000000-0000-0000-0000-000000000002',

    '00000000-0000-0000-0000-000000000004',

    '00000000-0000-0000-0000-000000000003',

    '10000000-0000-0000-0000-000000000002',

    'Banjara Hills, Hyderabad',
    17.4156,
    78.4347,

    'Gachibowli, Hyderabad',
    17.4401,
    78.3489,

    10.50,
    30,

    260.00,

    1.20,

    'pending',
    'accepted',

    NOW() - INTERVAL '10 minutes',
    NOW() - INTERVAL '7 minutes'
)

ON CONFLICT (ride_id) DO NOTHING;


-- ============================================================
-- 7. RIDE LOCATION HISTORY
-- ============================================================

INSERT INTO ride_locations (
    ride_id,
    driver_id,
    latitude,
    longitude,
    accuracy_meters,
    heading,
    speed_kmph,
    recorded_at
)
VALUES

(
    '30000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000003',
    17.4156,
    78.4347,
    8,
    90,
    0,
    NOW() - INTERVAL '6 minutes'
),

(
    '30000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000003',
    17.4200,
    78.4200,
    7,
    85,
    25,
    NOW() - INTERVAL '3 minutes'
),

(
    '30000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000003',
    17.4250,
    78.4050,
    6,
    80,
    30,
    NOW()
);


-- ============================================================
-- 8. DRIVER LOCATION / AVAILABILITY
-- ============================================================

INSERT INTO driver_locations (
    driver_id,
    latitude,
    longitude,
    heading,
    speed_kmph,
    availability_status
)
VALUES

(
    '00000000-0000-0000-0000-000000000002',
    17.3850,
    78.4867,
    90,
    25,
    'online'
),

(
    '00000000-0000-0000-0000-000000000003',
    17.4250,
    78.4050,
    80,
    30,
    'busy'
);


-- ============================================================
-- 9. FARE ESTIMATE
-- ============================================================

INSERT INTO fare_estimates (
    estimate_id,
    ride_id,
    base_fare,
    distance_fare,
    time_fare,
    surge_multiplier,
    surge_amount,
    discount_amount,
    taxes,
    total_fare,
    currency
)
VALUES
(
    '40000000-0000-0000-0000-000000000001',

    '30000000-0000-0000-0000-000000000002',

    50.00,
    150.00,
    40.00,
    1.20,
    48.00,
    0.00,
    28.00,
    316.00,
    'INR'
)

ON CONFLICT (estimate_id) DO NOTHING;


-- ============================================================
-- 10. PAYMENT
-- ============================================================

INSERT INTO payments (
    payment_id,
    ride_id,
    user_id,
    amount,
    currency,
    payment_method,
    provider,
    provider_payment_id,
    payment_status,
    paid_at
)
VALUES
(
    '50000000-0000-0000-0000-000000000001',

    '30000000-0000-0000-0000-000000000001',

    '00000000-0000-0000-0000-000000000001',

    335.00,

    'INR',

    'upi',

    'demo',

    'DEMO-PAYMENT-001',

    'success',

    NOW() - INTERVAL '60 minutes'
)

ON CONFLICT (payment_id) DO NOTHING;


-- ============================================================
-- 11. DRIVER EARNINGS
-- ============================================================

INSERT INTO driver_earnings (
    earning_id,
    driver_id,
    ride_id,
    gross_fare,
    platform_fee,
    incentives,
    net_earning
)
VALUES
(
    '60000000-0000-0000-0000-000000000001',

    '00000000-0000-0000-0000-000000000002',

    '30000000-0000-0000-0000-000000000001',

    335.00,

    67.00,

    20.00,

    288.00
)

ON CONFLICT (earning_id) DO NOTHING;


-- ============================================================
-- 12. RIDE MATCHES
-- ============================================================

INSERT INTO ride_matches (
    match_id,
    ride_id,
    driver_id,
    distance_km,
    eta_minutes,
    score,
    status
)
VALUES

(
    '70000000-0000-0000-0000-000000000001',

    '30000000-0000-0000-0000-000000000002',

    '00000000-0000-0000-0000-000000000003',

    1.8,

    5,

    0.94,

    'accepted'
),

(
    '70000000-0000-0000-0000-000000000002',

    '30000000-0000-0000-0000-000000000002',

    '00000000-0000-0000-0000-000000000002',

    3.2,

    9,

    0.72,

    'rejected'
)

ON CONFLICT (match_id) DO NOTHING;


-- ============================================================
-- 13. RATING
-- ============================================================

INSERT INTO ratings (
    rating_id,
    ride_id,
    from_user_id,
    to_user_id,
    rating_type,
    stars,
    review,
    tags
)
VALUES
(
    '80000000-0000-0000-0000-000000000001',

    '30000000-0000-0000-0000-000000000001',

    '00000000-0000-0000-0000-000000000001',

    '00000000-0000-0000-0000-000000000002',

    'passenger_to_driver',

    5,

    'Good driving and clean vehicle.',

    '["safe_driving", "clean_vehicle"]'::jsonb
)

ON CONFLICT (rating_id) DO NOTHING;


-- ============================================================
-- 14. SAFETY INCIDENT
-- ============================================================

INSERT INTO safety_incidents (
    incident_id,
    ride_id,
    reporter_id,
    reporter_type,
    target_user_id,
    incident_type,
    severity,
    description,
    location,
    latitude,
    longitude,
    vehicle_number,
    emergency,
    status
)
VALUES
(
    '90000000-0000-0000-0000-000000000001',

    '30000000-0000-0000-0000-000000000001',

    '00000000-0000-0000-0000-000000000001',

    'passenger',

    '00000000-0000-0000-0000-000000000002',

    'unsafe_driving',

    'medium',

    'Demo safety incident for testing.',

    'HITEC City, Hyderabad',

    17.4483,

    78.3915,

    'TS09AB1234',

    FALSE,

    'resolved'
)

ON CONFLICT (incident_id) DO NOTHING;


-- ============================================================
-- 15. SOS EVENT
-- ============================================================

INSERT INTO sos_events (
    sos_id,
    ride_id,
    user_id,
    driver_id,
    reporter_type,
    status,
    priority,
    reason,
    vehicle_number,

    initial_latitude,
    initial_longitude,

    current_latitude,
    current_longitude,

    notification_sent,
    admin_notified,
    escalation_count,

    created_at,
    updated_at,
    resolved_at
)
VALUES
(
    'A0000000-0000-0000-0000-000000000001',

    '30000000-0000-0000-0000-000000000001',

    '00000000-0000-0000-0000-000000000001',

    '00000000-0000-0000-0000-000000000002',

    'passenger',

    'resolved',

    'critical',

    'Demo SOS event for testing.',

    'TS09AB1234',

    17.4483,
    78.3915,

    17.4490,
    78.3920,

    TRUE,
    TRUE,
    1,

    NOW() - INTERVAL '1 day',

    NOW() - INTERVAL '23 hours',

    NOW() - INTERVAL '23 hours'
)

ON CONFLICT (sos_id) DO NOTHING;


-- ============================================================
-- 16. SOS LOCATION HISTORY
-- ============================================================

INSERT INTO sos_locations (
    sos_id,
    latitude,
    longitude,
    accuracy_meters,
    heading,
    speed_kmph,
    recorded_at
)
VALUES

(
    'A0000000-0000-0000-0000-000000000001',
    17.4483,
    78.3915,
    8,
    90,
    20,
    NOW() - INTERVAL '1 day'
),

(
    'A0000000-0000-0000-0000-000000000001',
    17.4487,
    78.3917,
    7,
    88,
    18,
    NOW() - INTERVAL '23 hours 59 minutes'
),

(
    'A0000000-0000-0000-0000-000000000001',
    17.4490,
    78.3920,
    6,
    85,
    15,
    NOW() - INTERVAL '23 hours'
);


-- ============================================================
-- 17. NOTIFICATIONS
-- ============================================================

INSERT INTO notifications (
    notification_id,
    user_id,
    ride_id,
    notification_type,
    channel,
    title,
    message,
    status,
    provider_message_id,
    sent_at
)
VALUES

(
    'B0000000-0000-0000-0000-000000000001',

    '00000000-0000-0000-0000-000000000001',

    '30000000-0000-0000-0000-000000000002',

    'ride_update',

    'push',

    'Ride Accepted',

    'Your RideX driver has accepted your ride.',

    'sent',

    'DEMO-PUSH-001',

    NOW() - INTERVAL '5 minutes'
),

(
    'B0000000-0000-0000-0000-000000000002',

    '00000000-0000-0000-0000-000000000001',

    '30000000-0000-0000-0000-000000000001',

    'payment',

    'push',

    'Payment Successful',

    'Your RideX payment was successful.',

    'sent',

    'DEMO-PUSH-002',

    NOW() - INTERVAL '60 minutes'
)

ON CONFLICT (notification_id) DO NOTHING;


-- ============================================================
-- 18. RIDE CANCELLATION
-- ============================================================

INSERT INTO ride_cancellations (
    cancellation_id,
    ride_id,
    cancelled_by,
    cancelled_by_type,
    reason,
    cancellation_fee
)
VALUES
(
    'C0000000-0000-0000-0000-000000000001',

    '30000000-0000-0000-0000-000000000002',

    '00000000-0000-0000-0000-000000000004',

    'passenger',

    'Demo cancellation record.',

    0.00
)

ON CONFLICT (cancellation_id) DO NOTHING;


-- ============================================================
-- 19. SUMMARY
-- ============================================================

COMMIT;


-- ============================================================
-- VERIFY SEED DATA
-- ============================================================

SELECT
    'users' AS table_name,
    COUNT(*) AS records
FROM users

UNION ALL

SELECT
    'drivers',
    COUNT(*)
FROM drivers

UNION ALL

SELECT
    'vehicles',
    COUNT(*)
FROM vehicles

UNION ALL

SELECT
    'rides',
    COUNT(*)
FROM rides

UNION ALL

SELECT
    'payments',
    COUNT(*)
FROM payments

UNION ALL

SELECT
    'ratings',
    COUNT(*)
FROM ratings

UNION ALL

SELECT
    'safety_incidents',
    COUNT(*)
FROM safety_incidents

UNION ALL

SELECT
    'sos_events',
    COUNT(*)
FROM sos_events

UNION ALL

SELECT
    'notifications',
    COUNT(*)
FROM notifications

ORDER BY table_name;
