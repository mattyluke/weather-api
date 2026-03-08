from django.db.models import Avg, ExpressionWrapper, FloatField
from django.db.models.functions import ExtractMonth

def get_koppen_name(code):
    names = {
        "Cfa": "Humid Subtropical",
        "Cfb": "Temperate Oceanic",
        "Cfc": "Subpolar Oceanic",
        "Csa": "Hot Mediterranean",
        "Csb": "Warm Mediterranean",
        "Cwa": "Monsoon influenced Subtropical",
        "Cwb": "Subtropical Highland",
        "Dfa": "Humid Continental, hot summer",
        "Dfb": "Humid Continental, warm summer",
        "Dfc": "Subarctic",
        "Dfd": "Extremely Cold Subarctic",
        "Dwa": "Monsoon Continental, hot summer",
        "Dwb": "Monsoon Continental, warm summer",
        "Dwc": "Monsoon Subarctic",
        "Dwd": "Extremely Cold Monsoon Subarctic",
        "Dsa": "Continental Mediterranean, hot summer",
        "Dsb": "Continental Mediterranean, warm summer",
        "Dsc": "Continental Subarctic, dry summer"
    }

    return names.get(code, "Unknown")

def get_koppen_desc(code):
    descriptions = {
        "Cfa": "Hot humid summers, mild winters, rainfall all year round",
        "Cfb": "Warm summers, mild winters, rainfall distributed throughout year",
        "Cfc": "Cool summers, mild winters, frequent rainfall",
        "Csa": "Hot dry summers, mild wet winters",
        "Csb": "Warm dry summers, mild wet winters",
        "Cwa": "Hot wet summers, dry mild winters",
        "Cwb": "Warm wet summers, dry mild winters, high altitude",
        "Dfa": "Hot summers, cold winters, precipitation year round",
        "Dfb": "Warm summers, cold winters, precipitation year round",
        "Dfc": "Cool summers, very cold winters, precipitation year round",
        "Dfd": "Cool summers, extremely cold winters",
        "Dwa": "Hot wet summers, cold dry winters",
        "Dwb": "Warm wet summers, cold dry winters",
        "Dwc": "Cool wet summers, very cold dry winters",
        "Dwd": "Cool wet summers, extremely cold dry winters",
        "Dsa": "Hot dry summers, cold winters",
        "Dsb": "Warm dry summers, cold winters",
        "Dsc": "Cool dry summers, cold winters"
    }

    return descriptions.get(code, "Unknown")

def calculate_koppen(records):
    monthly = (
        records
        .annotate(month=ExtractMonth('date'))
        .values('month')
        .annotate(
            avg_temp = ExpressionWrapper((Avg('maxtemp') + Avg('mintemp')) / 2, output_field = FloatField()),
            avg_precip = ExpressionWrapper(Avg('precipitation') * 30, output_field = FloatField()) # Average monthly
        )
        .order_by('month')
    )

    monthly_list = list(monthly)

    temps = [m['avg_temp'] for m in monthly_list]
    precips = [m['avg_precip'] for m in monthly_list]

    coldest = min(temps)
    warmest = max(temps)
    driest = min(precips)
    annual_precip = sum(precips)
    annual_temp = sum(temps) / 12
    months_above_10 = sum(1 for t in temps if t > 10)
    months_above_22 = sum(1 for t in temps if t > 22)

    sorted_months = sorted(range(12), key=lambda i: temps[i])
    winter_months = sorted_months[:6]
    summer_months = sorted_months[6:]

    summer_precip = sum(precips[i] for i in summer_months)
    winter_precip = sum(precips[i] for i in winter_months)

    # Check for polar (E)

    if warmest < 10:
        if warmest < 0:
            return {"code": "EF", "name": "Ice Cap", "description": "Eternal winter, all 12 months averaging below 0 degrees celsius"}
        return {"code": "ET", "name": "Tundra", "description": "Average temperature of warmest month between 0 degrees celsius and 10 degrees celsius"}
    
    # Check for arid (B)

    if summer_precip > winter_precip * 2:
        p_threshold = 20 * annual_temp + 280
    elif winter_precip > summer_precip * 2:
        p_threshold = 20 * annual_temp
    else:
        p_threshold = 20 * annual_temp + 140
    
    if annual_precip < p_threshold / 2:
        if annual_temp >= 18:
            return {"code": "BWh", "name": "Hot Desert", "description": "Very dry and hot all year round"}
        else:
            return {"code": "BWk", "name": "Cold Desert", "description": "Very dry and cold all year round"}
    
    if annual_precip < p_threshold:
        if annual_temp >= 18:
            return {"code": "BSh", "name": "Hot Steppe", "description": "Hot semi-arid climate"}
        else:
            return {"code": "BSk", "name": "Cold Steppe", "description": "Cold semi-arid climate"}
        
    # Check for tropical (A)

    if coldest > 18:
        if driest > 60:
            return {"code": "Af", "name": "Tropical Rainforest", "description": "Hot and wet all year round"}
        if driest > 100 - (annual_precip / 25):
            return {"code": "Am", "name": "Tropical Monsoon", "description": "Hot with a distinct monsoon season"}
        return {"code": "Aw", "name": "Tropical Savannah", "description": "Hot with distinct dry season"}
    
    # Check for temperate (C) or contintental (D)

    dry_summer = (
    max(precips[i] for i in winter_months) > 3 * min(precips[i] for i in summer_months)
        and min(precips[i] for i in summer_months) < 40
        and min(precips[i] for i in summer_months) > 1
    )

    dry_winter = (
        max(precips[i] for i in summer_months) > 10 * min(precips[i] for i in winter_months)
        and min(precips[i] for i in winter_months) > 3
    )

    if dry_summer:
        season = 's'
    elif dry_winter:
        season = 'w'
    else:
        season = 'f'

    if months_above_22 >= 1:
        temp_type = 'a'
    elif months_above_10 >= 4:
        temp_type = 'b'
    else:
        temp_type = 'c'

    if coldest > -3:
        return {
            "code": f"C{season}{temp_type}",
            "name": get_koppen_name(f"C{season}{temp_type}"),
            "description": get_koppen_desc(f"C{season}{temp_type}")
        }

    else:
        if coldest < -38:
            return {"code": f"D{season}d", "name": "Extreme Cold Continental", "description": "Very severe winters and boreal climate"}
        return {
            "code": f"D{season}{temp_type}",
            "name": get_koppen_name(f"D{season}{temp_type}"),
            "description": get_koppen_desc(f"D{season}{temp_type}")
        }