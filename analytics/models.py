from django.db import models


class Market(models.Model):
    city_name = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    region = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.city_name}, {self.state}"


class Submarket(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='submarkets')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.market.city_name})"


class PropertyType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Property(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='properties')
    submarket = models.ForeignKey(Submarket, on_delete=models.PROTECT, related_name='properties')
    property_type = models.ForeignKey(PropertyType, on_delete=models.PROTECT, related_name='properties')
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    sq_ft = models.IntegerField()
    units = models.IntegerField(default=1)
    year_built = models.IntegerField()
    acres = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2)

    # Rent input — changing this updates all report calculations
    market_rent_per_sqft = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    # Property-level income/expense inputs
    misc_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    annual_opex_reserve = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    annual_capx_reserve = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class Lease(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='leases')
    tenant_name = models.CharField(max_length=200)
    sq_ft_occupied = models.IntegerField()
    lease_start_date = models.DateField(default='2026-01-01')
    lease_end_date = models.DateField(default='2000-01-01')

    def __str__(self):
        return f"{self.tenant_name} - {self.property.name}"