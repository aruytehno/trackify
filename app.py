import folium
from flask import Flask, request, render_template
from config import Config
from services.sheets import get_addresses
from services.geocoder import geocode_address
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        # Получаем/обновляем склад
        warehouse_coords = Config.WAREHOUSE_COORDS
        warehouse_address = Config.WAREHOUSE_ADDRESS

        if request.method == 'POST':
            new_warehouse = request.form.get('warehouse', '').strip()
            if new_warehouse:
                if coords := geocode_address(new_warehouse):
                    warehouse_coords = coords[::-1]  # Преобразуем [lon,lat] → [lat,lon]
                    warehouse_address = new_warehouse
                    logger.info(f"Updated warehouse to: {warehouse_address} ({warehouse_coords})")
                else:
                    logger.warning(f"Failed to geocode warehouse address: {new_warehouse}")

        # Создаём карту с увеличенным размером
        m = folium.Map(
            location=warehouse_coords,
            zoom_start=12,
            width='100%',
            height='90vh',
            tiles='OpenStreetMap'
        )

        # Маркер склада
        folium.Marker(
            location=warehouse_coords,
            popup=f"<b>Склад</b><br>{warehouse_address}",
            icon=folium.Icon(color='green', icon='warehouse', prefix='fa')
        ).add_to(m)

        # Добавляем адреса доставки
        addresses = []
        successful_points = 0

        for address in get_addresses():
            if not address.get('address'):
                continue

            if coords := geocode_address(address['address']):
                folium.Marker(
                    location=coords[::-1],  # Преобразуем координаты
                    popup=f"<b>{address.get('company', 'Без названия')}</b><br>{address['address']}",
                    icon=folium.Icon(color='blue', icon='truck', prefix='fa')
                ).add_to(m)
                successful_points += 1
                addresses.append(address)
            else:
                logger.warning(f"Failed to geocode address: {address.get('address')}")

        logger.info(f"Map generated with {successful_points} points")

        return render_template(
            'index.html',
            map_html=m._repr_html_(),
            warehouse_address=warehouse_address,
            addresses=addresses
        )

    except Exception as e:
        logger.error(f"Error in index route: {str(e)}", exc_info=True)
        return render_template(
            'error.html',
            error_message="Произошла ошибка при загрузке карты"
        ), 500


if __name__ == '__main__':
    logger.info("Starting Trackify application")
    app.run(host='0.0.0.0', port=5000, debug=True)