-- day01.sql: practice database for Day 1 (SQLite; also works in MySQL/Postgres with tiny changes)
-- Run:  sqlite3 day01.db < day01.sql      then:  sqlite3 day01.db
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS transactions;

CREATE TABLE departments (
  id        INTEGER PRIMARY KEY,
  dept_name TEXT NOT NULL
);

CREATE TABLE employees (
  id        INTEGER PRIMARY KEY,
  name      TEXT NOT NULL,
  email     TEXT,
  dept_id   INTEGER REFERENCES departments(id),
  salary    INTEGER,
  city      TEXT,
  joined_on DATE
);

CREATE TABLE transactions (
  txn_id      INTEGER PRIMARY KEY,
  customer_id INTEGER,
  amount      REAL,
  status      TEXT,          -- SUCCESS / FAILED / PENDING
  created_at  DATE
);

INSERT INTO departments (id, dept_name) VALUES
  (10, 'SRE'), (20, 'Development'), (30, 'Support'), (40, 'Finance');

INSERT INTO employees (id, name, email, dept_id, salary, city, joined_on) VALUES
  (1, 'Asha',  'asha@corp.com',  10, 95000, 'Pune',      '2021-03-01'),
  (2, 'Ravi',  'ravi@corp.com',  20, 80000, 'Bengaluru', '2022-07-15'),
  (3, 'Meera', 'meera@corp.com', 10, 70000, 'Pune',      '2023-01-10'),
  (4, 'John',  'john@corp.com',  30, 55000, 'Mumbai',    '2020-11-20'),
  (5, 'Kiran', NULL,             20, 85000, 'Pune',      '2024-02-05'),
  (6, 'Neha',  'neha@corp.com',  NULL, 60000, 'Mumbai',  '2025-06-01'),
  (7, 'Amit',  'asha@corp.com',  30, 50000, 'Pune',      '2025-09-12');  -- duplicate email on purpose

INSERT INTO transactions (txn_id, customer_id, amount, status, created_at) VALUES
  (1001, 501, 2500.00, 'SUCCESS', '2026-11-10'),
  (1002, 502,  120.50, 'FAILED',  '2026-11-10'),
  (1003, 501, 9800.00, 'SUCCESS', '2026-11-11'),
  (1004, 503,   75.00, 'PENDING', '2026-11-11'),
  (1005, 504, 15000.0, 'SUCCESS', '2026-11-11'),
  (1006, 502,  300.00, 'FAILED',  '2026-11-12'),
  (1007, 505,  NULL,   'FAILED',  '2026-11-12');
