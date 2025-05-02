import os
import django
import random
from django.core.management.base import BaseCommand
import random
from core.models import Location

class Command(BaseCommand):
    help = 'Seed locations into the database'

    def handle(self, *args, **kwargs):
        
            Location.objects.all().delete()

            # Yaoundé Quarters
            yaounde_quarters = [
                'Essos', 'Bastos', 'Ngousso', 'Emana', 'Mvan', 'Nlongkak', 'Etoudi', 'Ahala',
                'Ekounou', 'Tsinga', 'Odza', 'Nkolbisson', 'Mendong', 'Biyem-Assi', 'Damas',
                'Nkoldongo', 'Carrefour Intendance', 'Elig-Edzoa', 'Nkomkana', 'Mvog-Ada',
                'Mvog-Betsi', 'Mfandena', 'Etoa-Meki', 'Efoulan', 'Obili'
            ]

            # Douala Quarters
            douala_quarters = [
                'Bonapriso', 'Akwa', 'Bonamoussadi', 'Logpom', 'Makepe', 'Deido', 'Ndokoti', 'Bepanda',
                'Bonanjo', 'Cité SIC', 'New-Bell', 'PK8', 'PK9', 'PK11', 'PK14', 'Ndogbong', 'Ndogpassi',
                'Nylon', 'Logbessou', 'Logbaba', 'Bonaberi', 'Kotto', 'Cité des Palmiers', 'Mboppi', 'Dakar'
            ]

            # Buea Quarters
            buea_quarters = [
                'Molyko', 'Great Soppo', 'Bonduma', 'Wotutu', 'Clerks Quarters', 'Small Soppo', 'Bakweri Town',
                'Wovia', 'Likoko Membea', 'Bokwaongo', 'Buea Town', 'Muea', 'Sandpit', 'Mile 17', 'Mile 16',
                'Mile 15', 'Mile 14', 'Bolifamba', 'Dibanda', 'GRA', 'Mile 18', 'Bonakanda', 'Bokwango', 'Wokoko',
                'Mile 19'
            ]

            # Bafoussam Quarters
            bafoussam_quarters = [
                'Banego', 'Djeleng', 'Tougang', 'Tamdja', 'Kamkop', 'Quartier Eveché', 'Marché A', 'Marché B',
                'Marché C', 'Ngouache', 'Nouvelle Route', 'Ngouache II', 'Kapsa', 'Tocket', 'Ngodo', 'Nkolbong',
                'Ndiangdam', 'Lafé-Baleng', 'Mairie', 'Famla', 'Tougang Nord', 'Tsiteng', 'Kamko', 'Ngouache III',
                'Bamendzi'
            ]

            # Base lat/lng for each town
            town_coords = {
                'Yaoundé': (3.8667, 11.5167),
                'Douala': (4.0500, 9.7000),
                'Buea': (4.1667, 9.2333),
                'Bafoussam': (5.4667, 10.4167)
            }

            # Compile everything
            locations = []

            for quarter in yaounde_quarters:
                lat, lng = town_coords['Yaoundé']
                locations.append(('Cameroon', 'Yaoundé', quarter, lat + random.uniform(-0.01, 0.01), lng + random.uniform(-0.01, 0.01)))

            for quarter in douala_quarters:
                lat, lng = town_coords['Douala']
                locations.append(('Cameroon', 'Douala', quarter, lat + random.uniform(-0.01, 0.01), lng + random.uniform(-0.01, 0.01)))

            for quarter in buea_quarters:
                lat, lng = town_coords['Buea']
                locations.append(('Cameroon', 'Buea', quarter, lat + random.uniform(-0.01, 0.01), lng + random.uniform(-0.01, 0.01)))

            for quarter in bafoussam_quarters:
                lat, lng = town_coords['Bafoussam']
                locations.append(('Cameroon', 'Bafoussam', quarter, lat + random.uniform(-0.01, 0.01), lng + random.uniform(-0.01, 0.01)))

            # Bulk create records
            bulk_data = [Location(
                country=country,
                town=town,
                quarter=quarter,
                latitude=latitude,
                longitude=longitude
            ) for (country, town, quarter, latitude, longitude) in locations]

            Location.objects.bulk_create(bulk_data)

            print(f"{len(bulk_data)} Locations seeded successfully.")
