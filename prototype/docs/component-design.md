# Component Design

## Project Name

Apartment Association Management System

## Main Components

### 1. User and Role Management Component

This component manages all system users and their roles.

Users include:

* Resident
* Owner
* Association Manager
* Maintenance Worker
* Treasurer/Admin

Main responsibilities:

* User login
* User registration
* Role-based access
* Profile management
* User activation/deactivation

Related tables:

* users
* memberships
* flats

---

### 2. Membership Management Component

This component manages apartment members and flat details.

Main responsibilities:

* Add new member
* Update member details
* Deactivate member
* Link member to flat
* Manage owner/tenant details
* View member list

Related tables:

* users
* flats
* memberships

---

### 3. Complaint and Maintenance Management Component

This component handles complaints raised by residents and maintenance work assigned by managers.

Main responsibilities:

* Raise complaint
* View complaint status
* Review complaint
* Assign worker
* Update complaint progress
* Close complaint after completion

Related tables:

* complaints
* complaint_assignments
* users
* flats

---

### 4. Invoice and Payment Tracking Component

This component handles invoice generation and payment status tracking.

Main responsibilities:

* Generate monthly maintenance invoice
* Generate complaint service invoice
* View invoice
* Track paid/unpaid status
* Mark invoice as paid
* Track pending dues

Related table:

* invoices

---

## Component Interaction

Resident users are managed through the User and Membership components. A resident can raise complaints through the Complaint and Maintenance component. The manager can assign the complaint to a worker. After the complaint is completed, an invoice can be generated if the service is chargeable. The Invoice component tracks whether the invoice is paid or unpaid.

## Summary

The system is divided into separate components to make it easier to design, develop, test, and maintain. Each component has a clear responsibility and can be improved in the future without affecting the whole system.
