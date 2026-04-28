from django.shortcuts import render, redirect
from django.db import connection


# ==========================================
# HELPER
# ==========================================
def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# ==========================================
# Create, read, update, delete for Properties
# ==========================================

def property_list(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.id, p.name, p.address,
                   pt.name AS property_type,
                   p.sq_ft, p.purchase_price,
                   p.market_rent_per_sqft,
                   m.city_name, m.state,
                   s.name AS submarket
            FROM analytics_property p
            JOIN analytics_market m ON p.market_id = m.id
            JOIN analytics_submarket s ON p.submarket_id = s.id
            JOIN analytics_propertytype pt ON p.property_type_id = pt.id
            ORDER BY p.name
        """)
        properties = dictfetchall(cursor)
    return render(request, 'analytics/property_list.html', {'properties': properties})


def property_add(request):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO analytics_property
                    (market_id, submarket_id, property_type_id, name, address,
                     sq_ft, units, year_built, acres, purchase_price,
                     market_rent_per_sqft, misc_income,
                     annual_opex_reserve, annual_capx_reserve)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                request.POST['market'],
                request.POST['submarket'],
                request.POST['property_type'],
                request.POST['name'],
                request.POST['address'],
                request.POST['sq_ft'],
                request.POST['units'],
                request.POST['year_built'],
                request.POST['acres'],
                request.POST['purchase_price'],
                request.POST['market_rent_per_sqft'],
                request.POST.get('misc_income', 0),
                request.POST.get('annual_opex_reserve', 0),
                request.POST.get('annual_capx_reserve', 0),
            ])
        return redirect('property_list')

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, city_name, state FROM analytics_market ORDER BY city_name")
        markets = dictfetchall(cursor)
        cursor.execute("SELECT id, name FROM analytics_propertytype ORDER BY name")
        property_types = dictfetchall(cursor)
        cursor.execute("SELECT id, name, market_id FROM analytics_submarket ORDER BY name")
        submarkets = dictfetchall(cursor)

    return render(request, 'analytics/property_form.html', {
        'markets': markets,
        'property_types': property_types,
        'submarkets': submarkets,
        'action': 'Add',
        'prop': {},
    })


def property_edit(request, pk):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM analytics_property WHERE id = %s", [pk])
        prop = dictfetchall(cursor)[0]
        cursor.execute("SELECT id, city_name, state FROM analytics_market ORDER BY city_name")
        markets = dictfetchall(cursor)
        cursor.execute("SELECT id, name FROM analytics_propertytype ORDER BY name")
        property_types = dictfetchall(cursor)
        cursor.execute("SELECT id, name, market_id FROM analytics_submarket ORDER BY name")
        submarkets = dictfetchall(cursor)

    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE analytics_property
                SET market_id=%s, submarket_id=%s, property_type_id=%s,
                    name=%s, address=%s, sq_ft=%s, units=%s,
                    year_built=%s, acres=%s, purchase_price=%s,
                    market_rent_per_sqft=%s, misc_income=%s,
                    annual_opex_reserve=%s, annual_capx_reserve=%s
                WHERE id=%s
            """, [
                request.POST['market'],
                request.POST['submarket'],
                request.POST['property_type'],
                request.POST['name'],
                request.POST['address'],
                request.POST['sq_ft'],
                request.POST['units'],
                request.POST['year_built'],
                request.POST['acres'],
                request.POST['purchase_price'],
                request.POST['market_rent_per_sqft'],
                request.POST.get('misc_income', 0),
                request.POST.get('annual_opex_reserve', 0),
                request.POST.get('annual_capx_reserve', 0),
                pk,
            ])
        return redirect('property_list')

    return render(request, 'analytics/property_form.html', {
        'prop': prop,
        'markets': markets,
        'property_types': property_types,
        'submarkets': submarkets,
        'action': 'Edit',
    })


def property_delete(request, pk):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM analytics_property WHERE id = %s", [pk])
        prop = dictfetchall(cursor)[0]

    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM analytics_lease WHERE property_id = %s", [pk])
            cursor.execute("DELETE FROM analytics_property WHERE id = %s", [pk])
        return redirect('property_list')

    return render(request, 'analytics/property_confirm_delete.html', {'prop': prop})

# ==========================================
# Report 
# ==========================================

def portfolio_report(request):
    # Dynamic dropdowns from DB (satisfies requirement 2c)
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, city_name, state FROM analytics_market ORDER BY city_name")
        markets = dictfetchall(cursor)
        cursor.execute("SELECT id, name FROM analytics_propertytype ORDER BY name")
        property_types = dictfetchall(cursor)
        cursor.execute("SELECT id, name, market_id FROM analytics_submarket ORDER BY name")
        submarkets = dictfetchall(cursor)

    selected_market_id = request.GET.get('market')
    selected_type_id = request.GET.get('property_type')
    selected_submarket_id = request.GET.get('submarket')

    filters = []
    params = []
    if selected_market_id:
        filters.append("p.market_id = %s")
        params.append(selected_market_id)
    if selected_type_id:
        filters.append("p.property_type_id = %s")
        params.append(selected_type_id)
    if selected_submarket_id:
        filters.append("p.submarket_id = %s")
        params.append(selected_submarket_id)

    where_clause = ("WHERE " + " AND ".join(filters)) if filters else ""

    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT
                p.id,
                p.name,
                m.city_name,
                m.state,
                pt.name AS property_type,
                s.name AS submarket,
                p.sq_ft,
                p.purchase_price,
                p.market_rent_per_sqft,
                p.misc_income,
                p.annual_opex_reserve,
                p.annual_capx_reserve,
                COALESCE(SUM(l.sq_ft_occupied), 0) AS occupied_sqft,
                -- PGI: full building at market rent annually
                ROUND(p.sq_ft * p.market_rent_per_sqft, 2) AS pgi,
                -- EGI: rent on only occupied sqft + misc income
                ROUND(
                    COALESCE(SUM(l.sq_ft_occupied), 0) * p.market_rent_per_sqft
                    + p.misc_income, 2
                ) AS egi,
                -- Total annual expenses
                ROUND(p.annual_opex_reserve + p.annual_capx_reserve, 2) AS total_expenses,
                -- NOI: EGI - expenses
                ROUND(
                    COALESCE(SUM(l.sq_ft_occupied), 0) * p.market_rent_per_sqft
                    + p.misc_income
                    - p.annual_opex_reserve
                    - p.annual_capx_reserve, 2
                ) AS noi,
                -- Cap rate: NOI / purchase price
                ROUND(
                    (
                        COALESCE(SUM(l.sq_ft_occupied), 0) * p.market_rent_per_sqft
                        + p.misc_income
                        - p.annual_opex_reserve
                        - p.annual_capx_reserve
                    ) / NULLIF(p.purchase_price, 0) * 100, 2
                ) AS cap_rate,
                -- Occupancy: occupied sqft / total sqft
                ROUND(
                    COALESCE(SUM(l.sq_ft_occupied), 0) * 100.0 / NULLIF(p.sq_ft, 0),
                2) AS occupancy_rate
            FROM analytics_property p
            JOIN analytics_market m ON p.market_id = m.id
            JOIN analytics_submarket s ON p.submarket_id = s.id
            JOIN analytics_propertytype pt ON p.property_type_id = pt.id
            LEFT JOIN analytics_lease l ON l.property_id = p.id
            {where_clause}
            GROUP BY p.id, p.name, m.city_name, m.state, pt.name, s.name,
                     p.sq_ft, p.purchase_price, p.market_rent_per_sqft,
                     p.misc_income, p.annual_opex_reserve, p.annual_capx_reserve
            ORDER BY p.name
        """, params)
        report_data = dictfetchall(cursor)

    # Portfolio-level summary stats
    avg_cap_rate = round(sum(r['cap_rate'] or 0 for r in report_data) / len(report_data), 2) if report_data else 0
    avg_occupancy = round(sum(r['occupancy_rate'] or 0 for r in report_data) / len(report_data), 2) if report_data else 0
    total_noi = round(sum(r['noi'] or 0 for r in report_data), 2)

    # Expiring leases
    days_filter = request.GET.get('expiring_within', '90')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                l.tenant_name,
                l.sq_ft_occupied,
                ROUND(l.sq_ft_occupied * p.market_rent_per_sqft, 2) AS annual_rent,
                l.lease_end_date,
                p.name AS property_name,
                m.city_name,
                CAST(julianday(l.lease_end_date) - julianday('now') AS INTEGER) AS days_until_expiry
            FROM analytics_lease l
            JOIN analytics_property p ON l.property_id = p.id
            JOIN analytics_market m ON p.market_id = m.id
            WHERE l.lease_end_date <= date('now', '+' || %s || ' days')
            AND l.lease_end_date >= date('now')
            ORDER BY l.lease_end_date ASC
        """, [days_filter])
        expiring_leases = dictfetchall(cursor)

    return render(request, 'analytics/portfolio_report.html', {
        'markets': markets,
        'property_types': property_types,
        'submarkets': submarkets,
        'report_data': report_data,
        'selected_market': selected_market_id,
        'selected_type': selected_type_id,
        'selected_submarket': selected_submarket_id,
        'avg_cap_rate': avg_cap_rate,
        'avg_occupancy': avg_occupancy,
        'total_noi': total_noi,
        'expiring_leases': expiring_leases,
        'days_filter': days_filter,
    })