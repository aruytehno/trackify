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

    // Добавляем маршруты для каждого автомобиля
    if (coordinates.routes) {
        Object.entries(coordinates.routes).forEach(([vehicleId, route]) => {
            if (route.geometry) {
                const routeGeometry = L.Polyline.fromEncoded(route.geometry, {
                    color: route.color || 'blue',
                    weight: 4,
                    opacity: 0.7,
                    smoothFactor: 1
                }).addTo(map);

                // Добавляем информацию о маршруте
                routeGeometry.bindPopup(`
                    <b>Автомобиль ${vehicleId}</b><br>
                    Остановок: ${route.stops_count}<br>
                    Общий вес: ${route.total_weight} кг
                `);
            }
        });
    }

function toggleVehicle(vehicleId, isActive) {
    fetch(`/toggle_vehicle/${vehicleId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({active: isActive})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        window.location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка при переключении автомобиля');
        // Вернуть переключатель в исходное состояние
        document.querySelector(`.vehicle-item[data-vehicle-id="${vehicleId}"] input[type="checkbox"]`).checked = !isActive;
    });
}

// Функция переключения аккордиона
function toggleAccordion(header) {
    const content = header.nextElementSibling;
    header.classList.toggle('collapsed');
    content.classList.toggle('expanded');

    // Автопрокрутка к только что открытой панели (необязательно)
    if (content.classList.contains('expanded')) {
        setTimeout(() => {
            header.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 300);
    }
}

// Опционально: при загрузке закрыть все аккордеоны:
// document.addEventListener('DOMContentLoaded', () => {
//   document.querySelectorAll('.accordion-header').forEach(h => h.classList.add('collapsed'));
// });
