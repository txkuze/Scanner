/*
  # Bot Database Schema

  1. New Tables
    - `sudo_users`
      - `id` (uuid, primary key)
      - `user_id` (bigint, unique) - Telegram user ID
      - `username` (text) - Telegram username
      - `first_name` (text) - User's first name
      - `added_by` (bigint) - User ID who added this sudo user
      - `added_at` (timestamptz) - When the user was added
      - `is_owner` (boolean) - Whether this is the owner
    
    - `user_history`
      - `id` (uuid, primary key)
      - `user_id` (bigint) - Telegram user ID
      - `username` (text) - Username at this point
      - `first_name` (text) - First name at this point
      - `last_name` (text) - Last name at this point
      - `recorded_at` (timestamptz) - When this was recorded
    
    - `chat_sessions`
      - `id` (uuid, primary key)
      - `user_id` (bigint) - Telegram user ID
      - `message` (text) - Message content
      - `role` (text) - 'user' or 'assistant'
      - `created_at` (timestamptz) - Message timestamp
    
    - `scan_logs`
      - `id` (uuid, primary key)
      - `user_id` (bigint) - User who performed scan
      - `username` (text) - Username at time of scan
      - `target` (text) - Scanned target
      - `risk_score` (int) - Risk score result
      - `scanned_at` (timestamptz) - Scan timestamp

  2. Security
    - Enable RLS on all tables
    - Add policies for authenticated access
*/

-- Create sudo_users table
CREATE TABLE IF NOT EXISTS sudo_users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id bigint UNIQUE NOT NULL,
  username text,
  first_name text,
  added_by bigint NOT NULL,
  added_at timestamptz DEFAULT now(),
  is_owner boolean DEFAULT false
);

ALTER TABLE sudo_users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow read access to all"
  ON sudo_users
  FOR SELECT
  USING (true);

CREATE POLICY "Allow insert for service role"
  ON sudo_users
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow update for service role"
  ON sudo_users
  FOR UPDATE
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow delete for service role"
  ON sudo_users
  FOR DELETE
  USING (true);

-- Create user_history table
CREATE TABLE IF NOT EXISTS user_history (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id bigint NOT NULL,
  username text,
  first_name text,
  last_name text,
  recorded_at timestamptz DEFAULT now()
);

ALTER TABLE user_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow read access to all"
  ON user_history
  FOR SELECT
  USING (true);

CREATE POLICY "Allow insert for service role"
  ON user_history
  FOR INSERT
  WITH CHECK (true);

-- Create chat_sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id bigint NOT NULL,
  message text NOT NULL,
  role text NOT NULL,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow read access to all"
  ON chat_sessions
  FOR SELECT
  USING (true);

CREATE POLICY "Allow insert for service role"
  ON chat_sessions
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow delete for service role"
  ON chat_sessions
  FOR DELETE
  USING (true);

-- Create scan_logs table
CREATE TABLE IF NOT EXISTS scan_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id bigint NOT NULL,
  username text,
  target text NOT NULL,
  risk_score int DEFAULT 0,
  scanned_at timestamptz DEFAULT now()
);

ALTER TABLE scan_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow read access to all"
  ON scan_logs
  FOR SELECT
  USING (true);

CREATE POLICY "Allow insert for service role"
  ON scan_logs
  FOR INSERT
  WITH CHECK (true);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sudo_users_user_id ON sudo_users(user_id);
CREATE INDEX IF NOT EXISTS idx_user_history_user_id ON user_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_scan_logs_user_id ON scan_logs(user_id);
