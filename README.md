# CRE Asset Management Platform
 
A database-backed web application for managing and analyzing a commercial real estate investment portfolio. Built with Django and SQLite as a semester project for CS348 at Purdue University.
 
## Overview
 
This application allows a real estate investor to track properties across multiple markets, manage tenant leases, and generate financial performance reports including NOI, cap rate, and occupancy metrics. A very simple application of computer science concepts and commercial real estate.
 
## Features
 
**Asset Management**
- Add, edit, and delete commercial properties
- Track key property attributes: market, submarket, property type, square footage, purchase price, and financial inputs
- All dropdown menus (market, submarket, property type) are populated dynamically from the database
**Portfolio Analytics Report**
- Filter properties by market, submarket, and property type
- View calculated financial metrics for each property:
  - Potential Gross Income (PGI)
  - Effective Gross Income (EGI)
  - Net Operating Income (NOI)
  - Cap Rate
  - Occupancy Rate
- Upcoming lease expiration tracker with configurable time window (30/90/180/365 days)
- Portfolio-level summary stats: total NOI, average cap rate, average occupancy
## Tech Stack
 
- **Backend:** Python, Django
- **Database:** SQLite
- **Frontend:** HTML, Bootstrap 5
- **Database Access:** Raw SQL via Django's `connection.cursor()`
## Database Schema
 
- `Market` — city, state, region
- `Submarket` — FK to Market
- `PropertyType` — Office, Retail, Industrial, Multifamily
- `Property` — FKs to Market, Submarket, PropertyType; stores financial inputs including `market_rent_per_sqft`
- `Lease` — FK to Property; stores tenant, sq ft occupied, and lease dates
Rent is stored on the `Property` model as `market_rent_per_sqft`. All income calculations (PGI, EGI, NOI, cap rate) are derived from this single field, so updating rent on a property instantly updates all report figures.
 
## Setup
 
```bash
# Clone the repo
git clone <your-repo-url>
cd CREAssetManagementPlatform
 
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
 
# Install dependencies
pip install django
 
# Run migrations
python manage.py makemigrations
python manage.py migrate
 
# Load sample data
python manage.py loaddata initial_data.json
 
# Create admin user
python manage.py createsuperuser
 
# Start the server
python manage.py runserver
```
 
Then visit the given link in your terminal.
 
## Project Structure
 
```
analytics/
├── fixtures/
│   └── initial_data.json       # Sample data: 4 markets, 9 properties, 16 leases
├── migrations/
├── templates/analytics/
│   ├── property_list.html
│   ├── property_form.html
│   ├── property_confirm_delete.html
│   └── portfolio_report.html
├── admin.py
├── models.py
├── urls.py
└── views.py
```
 