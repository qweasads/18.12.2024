CREATE DATABASE expense_tracker_db;
USE expense_tracker_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    password VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    amount DECIMAL(10, 2),
    category VARCHAR(100),
    type ENUM('income', 'expense'),
    created_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
