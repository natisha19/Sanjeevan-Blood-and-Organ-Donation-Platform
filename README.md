# 🩸 Sanjeevan – Blood & Organ Donation Management System

## 📘 Overview

**Sanjeevan** is a Streamlit-based web application that streamlines the process of **blood and organ donation management** across multiple hospitals.  
It connects **donors**, **recipients**, and **hospitals** through a unified digital platform, enabling compatibility checks, donor–recipient matching, and donation event management — all with database-driven validation.

---

## 🎯 Key Objectives

- Digitize donor and recipient records.
- Automate compatibility checks for blood and organ donations.
- Maintain donation event history.
- Ensure secure role-based access for admins and hospitals.
- Demonstrate advanced SQL concepts: functions, procedures, triggers, joins, aggregates, and nested queries.

---

## 🧩 Features

| Module | Features |
|--------|-----------|
| **Authentication** | Separate login for **Admin** and **Hospitals**, secure password hashing using SHA256 |
| **Admin Dashboard** | Manage hospitals, donors, recipients, and oversee compatibility & events |
| **Hospital Dashboard** | Perform compatibility checks, record donation events, view history |
| **Donor Module** | Register donors, update details, delete records |
| **Recipient Module** | Register recipients, assign urgency and required organ |
| **Compatibility Check** | Auto blood-group validation + manual organ compatibility confirmation |
| **Events Module** | Record and track blood & organ donation events |
| **Triggers & Procedures** | Demonstrates stored procedures, functions, and triggers via GUI |
| **SQL Queries Demo** | Nested, aggregate, and join queries implemented in the interface |

---

## 🧠 Database Design

### **Entities (Tables)**
1. `admin_users` – Admin credentials  
2. `hospital` – Hospital details  
3. `hospital_auth` – Hospital login credentials  
4. `donor` – Donor demographics and medical info  
5. `recipient` – Recipient information with urgency and organ need  
6. `blood_compatibility` – Blood match status and score  
7. `organ_compatibility` – Organ match status and score  
8. `blood_donation_event` – Blood donation tracking  
9. `organ_donation_event` – Organ donation tracking  

---

## 🧾 Normalization

All tables in the **Sanjeevan** database are normalized **up to Third Normal Form (3NF)**:

- Each attribute holds **atomic values**.  
- Every non-key attribute is **fully dependent** on its table’s primary key.  
- There are **no transitive dependencies** between non-key attributes.
