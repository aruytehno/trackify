document.addEventListener("DOMContentLoaded", function () {
    const coordinates = JSON.parse(document.getElementById('map-coordinates').textContent);
    const markerList = [];
    let map = null;

    const iframe = document.querySelector("#map iframe");

    if (iframe) {
        iframe.addEventListener("load", () => {
            const innerDoc = iframe.contentDocument || iframe.contentWindow.document;
            map = iframe.contentWindow.map_7e281b30fe648e76faa03c4bcd5a92a0;

            coordinates.forEach((coord, index) => {
                const marker = L.marker([coord.lat, coord.lon], {
                    icon: L.AwesomeMarkers.icon({
                        icon: 'truck',
                        prefix: 'fa',
                        markerColor: 'blue'
                    })
                }).addTo(map).bindPopup(coord.popup);

                markerList.push(marker);
            });
        });
    }

    window.highlightMarker = function(index) {
        document.querySelectorAll('.address-item').forEach(item => {
            item.classList.remove('highlighted');
        });
        document.querySelector(`.address-item[data-index="${index}"]`).classList.add('highlighted');

        if (!markerList.length || !map) return;

        markerList.forEach(m => m.setIcon(L.AwesomeMarkers.icon({
            icon: 'truck',
            prefix: 'fa',
            markerColor: 'blue'
        })));

        markerList[index].setIcon(L.AwesomeMarkers.icon({
            icon: 'truck',
            prefix: 'fa',
            markerColor: 'orange'
        }));

        map.setView(markerList[index].getLatLng(), 14);
        markerList[index].openPopup();
    };
});