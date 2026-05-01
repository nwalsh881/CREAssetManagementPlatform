#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# =============================================================================
# AI USAGE DISCLOSURE
# =============================================================================
# Tool Used: Claude (Anthropic)
#
# Tasks AI Assisted With:
#
# 1. DATABASE SCHEMA DESIGN
#    AI helped reason through the decision to move market_rent_per_sqft onto
#    the Property model rather than Lease, so that changing rent on a property
#    automatically updates NOI and cap rate calculations in the report.
#    AI also suggested converting submarket and property_type from hardcoded
#    text fields to FK relationships to satisfy the dynamic UI requirement.
#
# 2. SQL QUERY WRITING
#    AI helped write the main portfolio report query, specifically the NOI,
#    cap rate, and occupancy calculations using SQL aggregations and NULLIF
#    to avoid division by zero errors.
#
# 3. FIXTURE / SEED DATA
#    AI generated the initial_data.json fixture with realistic commercial
#    real estate properties, leases, and financial inputs across four markets.
#
# 4. DEBUGGING
#    AI helped diagnose the IntegrityError on property delete (missing cascade
#    delete of leases) and the migration error caused by existing string values
#    in the submarket column when converting it to a FK.
#
# 5. TEMPLATE STRUCTURE
#    AI assisted with Bootstrap layout for the report page and the cascading
#    submarket dropdown JavaScript that filters submarkets by selected market.
#
# How AI Output Was Verified and Modified:
#
# - All SQL queries were tested against the actual SQLite database and
#   results were verified manually against known fixture data.
# - Schema decisions were evaluated against project requirements before
#   implementing — for example, confirming that FK-based dropdowns satisfied
#   requirement 2c before adopting that approach.
# - The cascading submarket JS was tested in the browser across multiple
#   market selections to confirm correct filtering behavior.
# - Migration errors and integrity errors encountered during development
#   confirmed understanding of how Django handles FK constraints and
#   schema changes on existing data.
# - All code was reviewed line by line and can be explained independently
#   of AI assistance.
# =============================================================================

def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "managamentPlatform.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
