document.addEventListener("DOMContentLoaded", function () {
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

    window.highlightMarker = function(index) {
        // Убираем подсветку со всех адресов в списке
        document.querySelectorAll('.address-item').forEach(item => item.classList.remove('highlighted'));

        // Подсвечиваем кликнутый адрес
        const selectedAddress = document.querySelector(`.address-item[data-index="${index}"]`);
        if (selectedAddress) selectedAddress.classList.add('highlighted');

        // Проверяем что есть маркер с таким индексом (учитывая, что первый маркер — склад)
        // Так как склад — первый маркер, а доставки начинаются с индекса 1
        // индекс адреса из списка соответствует markerList индекс смещён на +1
        const markerIndex = index + 1;
        if (!markerList.length || !map || !markerList[markerIndex]) return;

        // Сбрасываем иконки всех маркеров (синий цвет)
        markerList.forEach(m => m.setIcon(L.AwesomeMarkers.icon({
            icon: 'truck',
            prefix: 'fa',
            markerColor: 'blue'
        })));

        // Подсвечиваем выбранный маркер (оранжевый)
        markerList[markerIndex].setIcon(L.AwesomeMarkers.icon({
            icon: 'truck',
            prefix: 'fa',
            markerColor: 'orange'
        }));

        // Центрируем карту на выбранном маркере
        map.setView(markerList[markerIndex].getLatLng(), 14);

        // Открываем попап
        markerList[markerIndex].openPopup();
    };
});
