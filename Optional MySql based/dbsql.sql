CREATE DATABASE banking_system;
USE banking_system;

CREATE TABLE accounts (
    account_number INT PRIMARY KEY,
    balance FLOAT NOT NULL
);

CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_number INT,
    type VARCHAR(20),
    amount FLOAT,
    balance_after FLOAT,
    counter INT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
-- Create a default user for the project (optional)
CREATE USER IF NOT EXISTS 'bankuser'@'localhost' IDENTIFIED BY 'Bankpass!';
GRANT ALL PRIVILEGES ON banking.* TO 'bankuser'@'localhost';
FLUSH PRIVILEGES;