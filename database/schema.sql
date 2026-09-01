-- ============================================================
-- RideX PostgreSQL Database Schema
-- ============================================================

-- ============================================================
-- EXTENSIONS
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- ============================================================
-- USERS
-- ============================================================

CREATE TABLE IF NOT EXISTS users (

    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    first_name VARCHAR(100) NOT NULL,

    last_name VARCHAR(100),

    email VARCHAR(255) UNIQUE,

    phone VARCHAR(30) UNIQUE NOT NULL,

    password_hash TEXT,

    role VARCHAR(30) NOT NULL DEFAULT 'passenger',

    status VARCHAR(30) NOT NULL DEFAULT 'active',

    profile_image_url TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT users_role_check
        CHECK (
            role IN (
                'passenger',
                'driver',
                'admin'
            )
        ),

    CONSTRAINT users_status_check
        CHECK (
            status IN (
                'active',
                'inactive',
                'blocked',
                'suspended'
            )
        )
);


-- ============================================================
-- DRIVER PROFILES
-- ============================================================

CREATE TABLE IF NOT EXISTS drivers (

    driver_id UUID PRIMARY KEY
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    license_number VARCHAR(100) UNIQUE NOT NULL,

    license_expiry DATE,

    vehicle_id UUID,

    driver_status VARCHAR(30)
        NOT NULL DEFAULT 'offline',

    verification_status VARCHAR(30)
        NOT NULL DEFAULT 'pending',

    current_latitude DOUBLE PRECISION,

    current_longitude DOUBLE PRECISION,

    current_heading DOUBLE PRECISION,

    current_speed_kmph DOUBLE PRECISION,

    last_location_update TIMESTAMPTZ,

    total_rides INTEGER NOT NULL DEFAULT 0,

    total_earnings NUMERIC(12,2)
        NOT NULL DEFAULT 0,

    average_rating NUMERIC(3,2)
        NOT NULL DEFAULT 0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT drivers_status_check
        CHECK (
            driver_status IN (
                'offline',
                'online',
                'busy',
                'suspended'
            )
        ),

    CONSTRAINT drivers_verification_check
        CHECK (
            verification_status IN (
                'pending',
                'verified',
                'rejected'
            )
        )
);


-- ============================================================
-- VEHICLES
-- ============================================================

CREATE TABLE IF NOT EXISTS vehicles (

    vehicle_id UUID PRIMARY KEY
        DEFAULT uuid_generate_v4(),

    driver_id UUID NOT NULL
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    vehicle_number VARCHAR(50) UNIQUE NOT NULL,

    make VARCHAR(100),

    model VARCHAR(100),

    year INTEGER,

    color VARCHAR(50),

    vehicle_type VARCHAR(50)
        NOT NULL DEFAULT 'car',

    capacity INTEGER
        NOT NULL DEFAULT 4,

    status VARCHAR(30)
        NOT NULL DEFAULT 'active',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- RIDES
-- ============================================================

CREATE TABLE IF NOT EXISTS rides (

    ride_id UUID PRIMARY KEY
        DEFAULT uuid_generate_v4(),

    passenger_id UUID NOT NULL
        REFERENCES users(user_id),

    driver_id UUID
        REFERENCES users(user_id),

    vehicle_id UUID
        REFERENCES vehicles(vehicle_id),

    pickup_address TEXT NOT NULL,

    pickup_latitude DOUBLE PRECISION NOT NULL,

    pickup_longitude DOUBLE PRECISION NOT NULL,

    destination_address TEXT NOT NULL,

    destination_latitude DOUBLE PRECISION NOT NULL,

    destination_longitude DOUBLE PRECISION NOT NULL,

    estimated_distance_km NUMERIC(10,2),

    estimated_duration_minutes INTEGER,

    actual_distance_km NUMERIC(10,2),

    actual_duration_minutes INTEGER,

    estimated_fare NUMERIC(12,2),

    final_fare NUMERIC(12,2),

    surge_multiplier NUMERIC(5,2)
        NOT NULL DEFAULT 1.0,

    payment_status VARCHAR(30)
        NOT NULL DEFAULT 'pending',

    ride_status VARCHAR(30)
        NOT NULL DEFAULT 'requested',

    requested_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),

    accepted_at TIMESTAMPTZ,

    started_at TIMESTAMPTZ,

    completed_at TIMESTAMPTZ,

    cancelled_at TIMESTAMPTZ,

    cancellation_reason TEXT,

    created_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW()
);


-- ============================================================
-- RIDE LOCATION HISTORY
-- ============================================================

CREATE TABLE IF NOT EXISTS ride_locations (

    location_id BIGSERIAL PRIMARY KEY,

    ride_id UUID NOT NULL
        REFERENCES rides(ride_id)
        ON DELETE CASCADE,

    driver_id UUID
        REFERENCES users(user_id),

    latitude DOUBLE PRECISION NOT NULL,

    longitude DOUBLE PRECISION NOT NULL,

    accuracy_meters DOUBLE PRECISION,

    heading DOUBLE PRECISION,

    speed_kmph DOUBLE PRECISION,

    recorded_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW()
);


-- ============================================================
-- FARE ESTIMATES
-- ============================================================

CREATE TABLE IF NOT EXISTS fare_estimates (

    estimate_id UUID PRIMARY KEY
        DEFAULT uuid_generate_v4(),

    ride_id UUID
        REFERENCES rides(ride_id)
        ON DELETE SET NULL,

    base_fare NUMERIC(12,2) NOT NULL,

    distance_fare NUMERIC(12,2)
        NOT NULL DEFAULT 0,

    time_fare NUMERIC(12,2)
        NOT NULL DEFAULT 0,

    surge_multiplier NUMERIC(5,2)
        NOT NULL DEFAULT 1.0,

    surge_amount NUMERIC(12,2)
        NOT NULL DEFAULT 0,

    discount_amount NUMERIC(12,2)
        NOT NULL DEFAULT 0,

    taxes NUMERIC(12,2)
        NOT NULL DEFAULT 0,

    total_fare NUMERIC(12,2)
        NOT NULL,

    currency VARCHAR(10)
        NOT NULL DEFAULT 'INR',

    created_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW()
);


-- ============================================================
-- PAYMENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS payments (

    payment_id UUID PRIMARY KEY
        DEFAULT uuid_generate_v4(),

    ride_id UUID NOT NULL
        REFERENCES rides(ride_id),

    user_id UUID NOT NULL
        REFERENCES users(user_id),

    amount NUMERIC(12,2) NOT NULL,

    currency VARCHAR(10)
        NOT NULL DEFAULT 'INR',

    payment_method VARCHAR(50),

    provider VARCHAR(50),

    provider_payment_id VARCHAR(255),

    payment_status VARCHAR(30)
        NOT NULL DEFAULT 'pending',

    failure_reason TEXT,

    paid_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW()
);


-- ============================================================
-- DRIVER EARNINGS
-- ============================================================

CREATE TABLE IF NOT EXISTS driver_earnings (

    earning_id UUID PRIMARY KEY
        DEFAULT uuid_generate_v4(),

    driver_id UUID NOT NULL
        REFERENCES users(user_id),

    ride_id UUID NOT NULL
        REFERENCES rides(ride_id),

    gross_fare NUMERIC(12,2) NOT NULL,

    platform_fee NUMERIC(12,2)
        NOT NULL DEFAULT 0,

    incentives NUMERIC(12,2)
        NOT NULL DEFAULT 0,

    net_earning NUMERIC(12,2)
        NOT NULL,

    created_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW()
);


-- ============================================================
-- RATINGS
-- ============================================================

CREATE TABLE IF NOT EXISTS ratings (

    rating_id UUID PRIMARY KEY
        DEFAULT uuid_generate_v4(),

    ride_id UUID NOT NULL
        REFERENCES rides(ride_id)
        ON DELETE CASCADE,

    from_user_id UUID NOT NULL
        REFERENCES users(user_id),

    to_user_id UUID NOT NULL
        REFERENCES users(user_id),

    rating_type VARCHAR(50) NOT NULL,

    stars INTEGER NOT NULL,

    review TEXT,

    tags JSONB,

    created_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),

    CONSTRAINT ratings_stars_check
        CHECK (
            stars BETWEEN 1 AND 5
        ),

    CONSTRAINT ratings_type_check
        CHECK (
            rating_type IN (
                'passenger_to_driver',
                'driver_to_passenger'
            )
        ),

    CONSTRAINT ratings_users_check
        CHECK (
            from_user_id <> to_user_id
        ),

    CONSTRAINT unique_ride_rating
        UNIQUE (
            ride_id,
            from_user_id,
            to_user_id
        )
);


-- ============================================================
-- SAFETY INCIDENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS safety_incidents (

    incident_id UUID PRIMARY KEY
        DEFAULT uuid_generate_v4(),

    ride_id UUID NOT NULL
        REFERENCES rides(ride_id),

    reporter_id UUID NOT NULL
        REFERENCES users(user_id),

    reporter_type VARCHAR(30) NOT NULL,

    target_user_id UUID
        REFERENCES users(user_id),

    incident_type VARCHAR(50) NOT NULL,

    severity VARCHAR(30) NOT NULL,

    description TEXT NOT NULL,

    location TEXT,

    latitude DOUBLE PRECISION,

    longitude DOUBLE PRECISION,

    vehicle_number VARCHAR(50),

    emergency BOOLEAN
        NOT NULL DEFAULT FALSE,

    status VARCHAR(30)
        NOT NULL DEFAULT 'open',

    created_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),

    resolved_at TIMESTAMPTZ
);


-- ============================================================
-- SAFETY EVIDENCE
-- ============================================================

CREATE TABLE IF NOT EXISTS safety_evidence (

    evidence_id UUID PRIMARY KEY
        DEFAULT uuid_generate_v4(),

    incident_id UUID NOT NULL
        REFERENCES safety_incidents(incident_id)
        ON DELETE CASCADE,

    evidence_type VARCHAR(50) NOT NULL,

    storage_reference TEXT NOT NULL,

    description TEXT,

    created_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW()
);


-- ============================================================
-- SOS EVENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS sos_events (

    sos_id UUID PRIMARY KEY
        DEFAULT uuid_generate_v4(),

    ride_id UUID NOT NULL
        REFERENCES rides(ride_id),

    user_id UUID NOT NULL
        REFERENCES users(user_id),

    driver_id UUID
        REFERENCES users(user_id),

    reporter_type VARCHAR(30) NOT NULL,

    status VARCHAR(30)
        NOT NULL DEFAULT 'activated',

    priority VARCHAR(30)
        NOT NULL DEFAULT 'critical',

    reason TEXT NOT NULL,

    vehicle_number VARCHAR(50),

    initial_latitude DOUBLE PRECISION NOT NULL,

    initial_longitude DOUBLE PRECISION NOT NULL,

    current_latitude DOUBLE PRECISION NOT NULL,

    current_longitude DOUBLE PRECISION NOT NULL,

    notification_sent BOOLEAN
        NOT NULL DEFAULT FALSE,

    admin_notified BOOLEAN
        NOT NULL DEFAULT FALSE,

    escalation_count INTEGER
        NOT NULL DEFAULT 0,

    created_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),

    resolved_at TIMESTAMPTZ
);


-- ============================================================
-- SOS LOCATION HISTORY
-- ============================================================

CREATE TABLE IF NOT EXISTS sos_locations (

    location_id BIGSERIAL PRIMARY KEY,

    sos_id UUID NOT NULL
        REFERENCES sos_events(sos_id)
        ON DELETE CASCADE,

    latitude DOUBLE PRECISION NOT NULL,

    longitude DOUBLE PRECISION NOT NULL,

    accuracy_meters DOUBLE PRECISION,

    heading DOUBLE PRECISION,

    speed_kmph DOUBLE PRECISION,

    recorded_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW()
);


-- ============================================================
-- EMERGENCY CONTACTS
-- ============================================================

CREATE TABLE IF NOT EXISTS emergency_contacts (

    contact_id UUID PRIMARY KEY
        DEFAULT uuid_generate_v4(),

    user_id UUID NOT NULL
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    contact_name VARCHAR(100) NOT NULL,

    phone VARCHAR(30) NOT NULL,

    relationship VARCHAR(50),

    is_primary BOOLEAN
        NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW()
);


-- ============================================================
-- NOTIFICATIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS notifications (

    notification_id UUID PRIMARY KEY
        DEFAULT uuid_generate_v4(),

    user_id UUID
        REFERENCES users(user_id)
        ON DELETE SET NULL,

    ride_id UUID
        REFERENCES rides(ride_id)
        ON DELETE SET NULL,

    notification_type VARCHAR(50) NOT NULL,

    channel VARCHAR(30) NOT NULL,

    title VARCHAR(255),

    message TEXT NOT NULL,

    status VARCHAR(30)
        NOT NULL DEFAULT 'pending',

    provider_message_id VARCHAR(255),

    error_message TEXT,

    sent_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW()
);


-- ============================================================
-- DRIVER LOCATION / AVAILABILITY
-- ============================================================

CREATE TABLE IF NOT EXISTS driver_locations (

    location_id BIGSERIAL PRIMARY KEY,

    driver_id UUID NOT NULL
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    latitude DOUBLE PRECISION NOT NULL,

    longitude DOUBLE PRECISION NOT NULL,

    heading DOUBLE PRECISION,

    speed_kmph DOUBLE PRECISION,

    availability_status VARCHAR(30)
        NOT NULL DEFAULT 'offline',

    recorded_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW()
);


-- ============================================================
-- RIDE MATCHING
-- ============================================================

CREATE TABLE IF NOT EXISTS ride_matches (

    match_id UUID PRIMARY KEY
        DEFAULT uuid_generate_v4(),

    ride_id UUID NOT NULL
        REFERENCES rides(ride_id)
        ON DELETE CASCADE,

    driver_id UUID NOT NULL
        REFERENCES users(user_id),

    distance_km NUMERIC(10,2),

    eta_minutes INTEGER,

    score NUMERIC(10,4),

    status VARCHAR(30)
        NOT NULL DEFAULT 'offered',

    offered_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),

    responded_at TIMESTAMPTZ
);


-- ============================================================
-- CANCELLATIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS ride_cancellations (

    cancellation_id UUID PRIMARY KEY
        DEFAULT uuid_generate_v4(),

    ride_id UUID NOT NULL
        REFERENCES rides(ride_id)
        ON DELETE CASCADE,

    cancelled_by UUID NOT NULL
        REFERENCES users(user_id),

    cancelled_by_type VARCHAR(30) NOT NULL,

    reason TEXT,

    cancellation_fee NUMERIC(12,2)
        NOT NULL DEFAULT 0,

    created_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW()
);


-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_users_phone
ON users(phone);

CREATE INDEX IF NOT EXISTS idx_users_email
ON users(email);

CREATE INDEX IF NOT EXISTS idx_users_role
ON users(role);

CREATE INDEX IF NOT EXISTS idx_drivers_status
ON drivers(driver_status);

CREATE INDEX IF NOT EXISTS idx_drivers_location
ON drivers(
    current_latitude,
    current_longitude
);

CREATE INDEX IF NOT EXISTS idx_rides_passenger
ON rides(passenger_id);

CREATE INDEX IF NOT EXISTS idx_rides_driver
ON rides(driver_id);

CREATE INDEX IF NOT EXISTS idx_rides_status
ON rides(ride_status);

CREATE INDEX IF NOT EXISTS idx_rides_requested
ON rides(requested_at);

CREATE INDEX IF NOT EXISTS idx_ride_locations_ride
ON ride_locations(ride_id);

CREATE INDEX IF NOT EXISTS idx_driver_locations_driver
ON driver_locations(driver_id);

CREATE INDEX IF NOT EXISTS idx_driver_locations_time
ON driver_locations(recorded_at);

CREATE INDEX IF NOT EXISTS idx_payments_ride
ON payments(ride_id);

CREATE INDEX IF NOT EXISTS idx_payments_user
ON payments(user_id);

CREATE INDEX IF NOT EXISTS idx_payments_status
ON payments(payment_status);

CREATE INDEX IF NOT EXISTS idx_ratings_to_user
ON ratings(to_user_id);

CREATE INDEX IF NOT EXISTS idx_ratings_ride
ON ratings(ride_id);

CREATE INDEX IF NOT EXISTS idx_safety_ride
ON safety_incidents(ride_id);

CREATE INDEX IF NOT EXISTS idx_safety_reporter
ON safety_incidents(reporter_id);

CREATE INDEX IF NOT EXISTS idx_safety_status
ON safety_incidents(status);

CREATE INDEX IF NOT EXISTS idx_sos_ride
ON sos_events(ride_id);

CREATE INDEX IF NOT EXISTS idx_sos_user
ON sos_events(user_id);

CREATE INDEX IF NOT EXISTS idx_sos_status
ON sos_events(status);

CREATE INDEX IF NOT EXISTS idx_sos_location_time
ON sos_locations(recorded_at);

CREATE INDEX IF NOT EXISTS idx_notifications_user
ON notifications(user_id);

CREATE INDEX IF NOT EXISTS idx_notifications_status
ON notifications(status);

CREATE INDEX IF NOT EXISTS idx_ride_matches_ride
ON ride_matches(ride_id);

CREATE INDEX IF NOT EXISTS idx_ride_matches_driver
ON ride_matches(driver_id);


-- ============================================================
-- SAMPLE ADMIN USER
-- ============================================================

INSERT INTO users (
    first_name,
    last_name,
    email,
    phone,
    role,
    status
)
VALUES (
    'RideX',
    'Admin',
    'admin@ridex.example',
    '+910000000000',
    'admin',
    'active'
)
ON CONFLICT DO NOTHING;


-- ============================================================
-- SCHEMA COMPLETE
-- ============================================================

SELECT
    'RideX database schema created successfully'
    AS message;
