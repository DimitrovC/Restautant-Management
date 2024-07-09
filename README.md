# Restaurant Management System

A comprehensive system for easy restaurant management, featuring seamless reservation making, interactive menus, an intuitive admin panel, and more. This project is built using Python Flask, HTML/CSS/JS, SQLite, and Tailwind CSS to provide a modern, efficient, and user-friendly experience.

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)

## Description

This Restaurant Management System is designed to simplify and enhance the management of restaurant operations. It allows for easy reservation making, provides dynamic and interactive menus, and includes an admin panel for efficient management of restaurant details and operations.

## Features

- **Reservation Making**: Easily manage table reservations with a user-friendly interface.
- **Interactive Menus**: Dynamic and customizable menus that enhance the dining experience.
- **Admin Panel**: Intuitive and powerful admin panel for managing restaurant operations.
- **Real-Time Updates**: Keep track of reservations, menu changes, and other updates in real time.

## Technologies Used

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **Styling**: Tailwind CSS

## Installation

Follow these steps to set up the project locally:

1. **Clone the repository**:
  ```bash
  git clone https://github.com/DimitrovC/Restautant-Management.git
  cd Restautant-Management
  ```

2. **Create a virtual environment**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
3. **Install the required packages**:
  ```bash
  pip install -r requirements.txt
  ```

4. **Set up the database**:
  ```bash
  flask db init
  flask db migrate -m "Initial migration."
  flask db upgrade
  ```

5. **Run the application**:
  ```bash
  flask run
  ```
