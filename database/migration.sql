-- ============================================================
-- CyberTrack v2.0 — Migration SQL
-- Run this in your Supabase project → SQL Editor
-- Adds new columns to existing tables WITHOUT dropping data
-- ============================================================

-- Add disguise and redirect_url to tracking_links
ALTER TABLE tracking_links ADD COLUMN IF NOT EXISTS disguise     TEXT DEFAULT 'default';
ALTER TABLE tracking_links ADD COLUMN IF NOT EXISTS redirect_url TEXT DEFAULT 'https://www.google.com';

-- Add fingerprint columns to tracking_logs
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS canvas_hash          TEXT;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS webgl_vendor         TEXT;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS webgl_renderer       TEXT;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS audio_hash           TEXT;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS fonts_hash           TEXT;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS color_depth          INT;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS pixel_ratio          FLOAT;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS screen_avail_w       INT;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS screen_avail_h       INT;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS touch_support        BOOLEAN;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS max_touch_points     INT;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS hardware_concurrency INT;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS device_memory        FLOAT;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS timezone_offset      INT;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS timezone_name        TEXT;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS has_ad_blocker       BOOLEAN;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS is_incognito         BOOLEAN;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS battery_level        FLOAT;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS battery_charging     BOOLEAN;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS webrtc_local_ip      TEXT;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS plugins             TEXT;
ALTER TABLE tracking_logs ADD COLUMN IF NOT EXISTS gpu_info            TEXT;
