-- public.admins definition

-- Drop table

-- DROP TABLE public.admins;

CREATE TABLE public.admins (
	admin_id uuid DEFAULT gen_random_uuid() NOT NULL,
	full_name varchar NOT NULL,
	email varchar NOT NULL,
	phone_no varchar NULL,
	password_hash text NOT NULL,
	"role" varchar DEFAULT 'SUPER_ADMIN'::character varying NULL,
	is_active bool DEFAULT true NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT admins_email_key UNIQUE (email),
	CONSTRAINT admins_phone_no_key UNIQUE (phone_no),
	CONSTRAINT admins_pkey PRIMARY KEY (admin_id)
);


-- public.users definition

-- Drop table

-- DROP TABLE public.users;

CREATE TABLE public.users (
	user_id uuid DEFAULT gen_random_uuid() NOT NULL,
	full_name varchar NOT NULL,
	phone_no varchar NOT NULL,
	email varchar NULL,
	"password" text NOT NULL,
	is_active bool DEFAULT true NULL,
	is_verified bool DEFAULT false NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT users_email_key UNIQUE (email),
	CONSTRAINT users_phone_no_key UNIQUE (phone_no),
	CONSTRAINT users_pkey PRIMARY KEY (user_id)
);


-- public.vendors definition

-- Drop table

-- DROP TABLE public.vendors;

CREATE TABLE public.vendors (
	vendor_id uuid DEFAULT gen_random_uuid() NOT NULL,
	is_active bool DEFAULT true NULL,
	vendor_full_name varchar NOT NULL,
	vendor_phone_no varchar NULL,
	vendor_email_id varchar NULL,
	vendor_address text NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	"password" varchar NULL,
	is_verified bool DEFAULT false NULL,
	CONSTRAINT vendors_pkey PRIMARY KEY (vendor_id),
	CONSTRAINT vendors_vendor_email_id_key UNIQUE (vendor_email_id),
	CONSTRAINT vendors_vendor_phone_no_key UNIQUE (vendor_phone_no)
);


-- public.turf_fields definition

-- Drop table

-- DROP TABLE public.turf_fields;

CREATE TABLE public.turf_fields (
	turf_field_id uuid DEFAULT gen_random_uuid() NOT NULL,
	turf_name varchar NOT NULL,
	turf_location text NULL,
	turf_address text NULL,
	no_of_grounds int4 NULL,
	vendor_id uuid NOT NULL,
	is_active bool DEFAULT true NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	turf_facilities text NULL,
	turf_rules text NULL,
	turf_images text NULL,
	latitude numeric(9, 6) NULL,
	longitude numeric(9, 6) NULL,
	CONSTRAINT turf_fields_pkey PRIMARY KEY (turf_field_id),
	CONSTRAINT turf_fields_vendor_id_fkey FOREIGN KEY (vendor_id) REFERENCES public.vendors(vendor_id) ON DELETE CASCADE
);


-- public.turf_grounds definition

-- Drop table

-- DROP TABLE public.turf_grounds;

CREATE TABLE public.turf_grounds (
	turf_ground_id uuid DEFAULT gen_random_uuid() NOT NULL,
	ground_name varchar NOT NULL,
	ground_loc text NULL,
	ground_type varchar NULL,
	turf_field_id uuid NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	ground_images text NULL,
	is_active bool DEFAULT true NULL,
	booking_weeks int4 DEFAULT 1 NULL,
	CONSTRAINT turf_grounds_pkey PRIMARY KEY (turf_ground_id),
	CONSTRAINT turf_grounds_turf_field_id_fkey FOREIGN KEY (turf_field_id) REFERENCES public.turf_fields(turf_field_id) ON DELETE CASCADE
);


-- public.turf_slots definition

-- Drop table

-- DROP TABLE public.turf_slots;

CREATE TABLE public.turf_slots (
	slot_id uuid DEFAULT gen_random_uuid() NOT NULL,
	turf_ground_id uuid NOT NULL,
	start_time time NOT NULL,
	end_time time NOT NULL,
	price numeric(10, 2) NOT NULL,
	is_peak bool DEFAULT false NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	day_of_week varchar NOT NULL,
	is_available bool DEFAULT true NULL,
	CONSTRAINT turf_slots_pkey PRIMARY KEY (slot_id),
	CONSTRAINT unique_slot UNIQUE (turf_ground_id, day_of_week, start_time),
	CONSTRAINT turf_slots_turf_ground_id_fkey FOREIGN KEY (turf_ground_id) REFERENCES public.turf_grounds(turf_ground_id) ON DELETE CASCADE
);


-- public.bookings definition

-- Drop table

-- DROP TABLE public.bookings;

CREATE TABLE public.bookings (
	booking_id uuid DEFAULT gen_random_uuid() NOT NULL,
	slot_id uuid NOT NULL,
	user_id uuid NULL,
	booking_status varchar DEFAULT 'CONFIRMED'::character varying NULL,
	booked_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	booking_date date DEFAULT CURRENT_DATE NOT NULL,
	is_available bool DEFAULT true NULL,
	razorpay_order_id varchar NULL,
	razorpay_payment_id varchar NULL,
	payment_status varchar DEFAULT 'PENDING'::character varying NULL,
	CONSTRAINT bookings_pkey PRIMARY KEY (booking_id),
	CONSTRAINT bookings_slot_id_fkey FOREIGN KEY (slot_id) REFERENCES public.turf_slots(slot_id) ON DELETE CASCADE
);
CREATE INDEX idx_bookings_slot ON public.bookings USING btree (slot_id);