import random
from datetime import datetime
from typing import Dict

from mimesis import Generic
from mimesis.enums import Gender, Locale
from mimesis.providers.finance import Finance


async def generate_details(locale: Locale) -> Dict[str, str]:
    generic = Generic(locale)
    gender = random.choice([Gender.MALE, Gender.FEMALE])
    finance_business_data_gen = Finance(locale)
    first_name = generic.person.first_name(gender=gender)
    last_name = generic.person.last_name(gender=gender)
    current_year = datetime.now().year
    age = random.randint(18, 50)
    birth_year = current_year - age
    birth_date = generic.datetime.date(start=birth_year, end=birth_year).strftime(
        "%Y-%m-%d"
    )
    details = {
        "Full Name": f"{first_name} {last_name}",
        "First Name": first_name,
        "Last Name": last_name,
        "Age": age,
        "Birth Date": birth_date,
        "Sex": generic.person.sex(),
        "University": generic.person.university(),
        "Street Name": generic.address.street_name(),
        "Street Number": generic.address.street_number(),
        "State": generic.address.state(),
        "City": generic.address.city(),
        "Country": generic.address.default_country(),
        "Postal Code": generic.address.postal_code(),
        "Company": finance_business_data_gen.company(),
        "Phone Number": generic.person.telephone(),
        "Occupation": generic.person.occupation(),
        "Nationality": generic.person.nationality(),
        "Language": generic.person.language(),
        "Username": generic.person.username(),
        "Password": generic.person.password(),
        "Weight": f"{generic.person.weight()} kg",
        "Height": f"{generic.person.height()} cm",
    }

    return details
