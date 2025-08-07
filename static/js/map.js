document.addEventListener("DOMContentLoaded", function() {
    // Проверка наличия карты
    if (typeof map === 'undefined') {
        console.error('Leaflet map not initialized');
        return;
    }

    // Получение данных координат
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

    // Очистка существующих маркеров
    map.eachLayer(layer => {
        if (layer instanceof L.Marker) {
            map.removeLayer(layer);
        }
    });

    // Добавление маркера склада
    if (coordinates.warehouse) {
        L.marker([coordinates.warehouse.lat, coordinates.warehouse.lon], {
            icon: L.AwesomeMarkers.icon({
                icon: 'warehouse',
                prefix: 'fa',
                markerColor: 'green'
            })
        }).bindPopup(coordinates.warehouse.popup).addTo(map);
    }

    // Добавление маркеров доставки
    if (coordinates.deliveries && coordinates.deliveries.length > 0) {
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
    }

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