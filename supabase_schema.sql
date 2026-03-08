-- SQL Schema for TruthLens Supabase setup

-- Enable UUID extension if not enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- USERS TABLE
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    phone TEXT,
    bio TEXT,
    linked_in TEXT,
    profile_photo TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    otp_code TEXT,
    otp_delete TEXT,
    analyses_count INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deletion_at TIMESTAMP WITH TIME ZONE -- NULL means no pending deletion
);

-- ANALYSES TABLE
CREATE TABLE IF NOT EXISTS public.analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id TEXT NOT NULL,
    claim TEXT NOT NULL,
    clean_claim TEXT NOT NULL,
    score INT NOT NULL,
    verdict TEXT NOT NULL,
    confidence INT NOT NULL,
    summary TEXT,
    hindi_summary TEXT,
    flags JSONB DEFAULT '[]'::jsonb,
    sources JSONB DEFAULT '[]'::jsonb,
    meta JSONB DEFAULT '{}'::jsonb,
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    ip_address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS (Row Level Security) - Optional but good for security
-- For hackathon, you can leave RLS disabled, or run these to allow public inserts
-- ALTER TABLE public.users DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.analyses DISABLE ROW LEVEL SECURITY;
