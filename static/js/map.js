document.addEventListener("DOMContentLoaded", function() {
    // Получаем данные координат
    const coordinatesData = document.getElementById('map-coordinates');
    if (!coordinatesData) {
        console.error('Element with map coordinates not found');
        return;
    }

    let coordinates;
    try {
        coordinates = JSON.parse(coordinatesData.textContent);
    } catch (e) {
        console.error('Error parsing coordinates:', e);
        return;
    }

    // Удаляем карту, созданную Folium (если есть)
    const mapContainer = document.getElementById('map');
    if (mapContainer._leaflet_map) {
        mapContainer._leaflet_map.remove();
    }

    // Создаем новую карту Leaflet
    const map = L.map('map').setView(
        [coordinates.warehouse.lat, coordinates.warehouse.lon],
        12
    );

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Добавляем маркер склада
    L.marker([coordinates.warehouse.lat, coordinates.warehouse.lon], {
        icon: L.AwesomeMarkers.icon({
            icon: 'warehouse',
            prefix: 'fa',
            markerColor: 'green'
        })
    }).bindPopup(coordinates.warehouse.popup).addTo(map);

    // Добавляем маркеры доставки
    coordinates.deliveries.forEach((delivery, index) => {
        L.marker([delivery.lat, delivery.lon], {
            icon: L.AwesomeMarkers.icon({
                icon: 'truck',
                prefix: 'fa',
                markerColor: 'blue'
            })
        }).bindPopup(delivery.popup)
         .addTo(map)
         .on('click', function() {
             highlightMarker(index);
         });
    });

    // Функция для подсветки маркера
    window.highlightMarker = function(index) {
        const markers = [];
        map.eachLayer(layer => {
            if (layer instanceof L.Marker && layer.options.icon.options.icon === 'truck') {
                markers.push(layer);
            }
        });

        if (index >= 0 && index < markers.length) {
            markers.forEach(marker => {
                marker.setIcon(L.AwesomeMarkers.icon({
                    icon: 'truck',
                    prefix: 'fa',
                    markerColor: 'blue'
                }));
            });

            markers[index].setIcon(L.AwesomeMarkers.icon({
                icon: 'truck',
                prefix: 'fa',
                markerColor: 'orange'
            }));

            map.setView(markers[index].getLatLng(), 14);
            markers[index].openPopup();
        }
    };
});