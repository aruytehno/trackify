document.addEventListener("DOMContentLoaded", function() {
    // Получаем координаты из скрытого JSON
    const coordinates = JSON.parse(document.getElementById('map-coordinates').textContent);

    const markerList = [];

    // Leaflet карта, создаваемая Folium, глобально доступна как переменная map
    // Собираем все маркеры, добавленные Folium (в т.ч. склад и доставки)
    map.eachLayer(function(layer) {
        if (layer instanceof L.Marker) {
            markerList.push(layer);
        }
    });

    // Функция для подсветки маркера
    window.highlightMarker = function(index) {
        // Убираем подсветку со всех адресов в списке
        document.querySelectorAll('.address-item').forEach(item => {
            item.classList.remove('highlighted');
        });

        // Подсвечиваем кликнутый адрес
        const selectedAddress = document.querySelector(`.address-item[data-index="${index}"]`);
        if (selectedAddress) {
            selectedAddress.classList.add('highlighted');
        }

        // Проверяем что есть маркер с таким индексом
        const markerIndex = index + 1; // +1 потому что первый маркер - склад
        if (!markerList.length || !map || !markerList[markerIndex]) return;

        // Сбрасываем иконки всех маркеров
        markerList.forEach(m => {
            m.setIcon(L.AwesomeMarkers.icon({
                icon: 'truck',
                prefix: 'fa',
                markerColor: 'blue'
            }));
        });

        // Подсвечиваем выбранный маркер
        markerList[markerIndex].setIcon(L.AwesomeMarkers.icon({
            icon: 'truck',
            prefix: 'fa',
            markerColor: 'orange'
        }));

        // Центрируем карту и открываем попап
        map.setView(markerList[markerIndex].getLatLng(), 14);
        markerList[markerIndex].openPopup();
    };

    // Обработка кликов по автомобилям
    document.querySelectorAll('.vehicle-item').forEach(item => {
        item.addEventListener('click', function() {
            const vehicleId = this.dataset.vehicleId;

            // Подсвечиваем выбранный автомобиль
            document.querySelectorAll('.vehicle-item').forEach(i => {
                i.classList.remove('active');
            });
            this.classList.add('active');

            // Показываем только маршрут этого автомобиля
            map.eachLayer(layer => {
                if (layer instanceof L.PolyLine) {
                    if (layer.options.popup === `Автомобиль ${vehicleId}`) {
                        layer.setStyle({opacity: 0.7, weight: 5});
                    } else {
                        layer.setStyle({opacity: 0.2, weight: 2});
                    }
                }
            });
        });
    });
});