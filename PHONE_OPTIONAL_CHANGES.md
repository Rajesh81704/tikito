# Phone Number Optional - Backend Changes

## Summary
Made phone number optional for user registration on the Tikito backend.

## Changes Applied

### 1. Database Schema (`ddl.sql`)
- Changed `phone_no` column from `NOT NULL` to `NULL` in the `users` table
- UNIQUE constraint on `phone_no` remains active (if provided, must be unique)

### 2. Database Migration
- Created and executed migration script: `migrate_phone_optional.py`
- Successfully altered the `users` table in the database
- Migration applied on: 2026-06-30

### 3. API Models (`app/api/user/controllers/user_controller.py`)
- Updated `CreateUser` Pydantic model
- Changed `phone_no: str` to `phone_no: str | None = None`

### 4. Response Models (`app/api/auth/auth_controller.py`)
- Updated `UserMeSchema` Pydantic model
- Changed `phone_no: str` to `phone_no: str | None = None`

### 5. Service Logic (`app/api/user/services/user_service.py`)
- Updated `create()` function to handle optional phone number
- Added validation: at least one of email or phone must be provided
- Dynamic query building for duplicate checking (only checks provided fields)

## Validation Rules

Users can now register with:
- ✅ Phone number only
- ✅ Email only
- ✅ Both phone and email
- ❌ Neither (will return error: "Either phone number or email must be provided")

## Database Constraints
- Phone numbers must be unique if provided
- Emails must be unique if provided
- At least one identifier (phone or email) is required at the application level

## Testing Recommendations

Test the following scenarios:
1. Register with phone number only
2. Register with email only
3. Register with both phone and email
4. Try to register without both (should fail)
5. Try to register with duplicate phone (should fail)
6. Try to register with duplicate email (should fail)
