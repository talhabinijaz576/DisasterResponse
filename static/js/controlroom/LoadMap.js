var mymap;
var oms;
var clusterMarkers = L.markerClusterGroup();
function traffic_simulate() {
    mymap = L.map('mapid', {   // Then add it here..
        maxZoom: 19,
        minZoom: 14
    }).setView([53.4029809620105, -6.30429581584211], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap contributors</a>'
    }).addTo(mymap);
    oms = new OverlappingMarkerSpiderfier(mymap);
    //mymap.setMaxBounds(bounds);
    //L.marker([53.3498, -6.2603], {icon: greenIcon}).addTo(mymap).bindPopup("I am a green leaf.");

    mymap.on("click", function (e) {
        document.getElementById("lat").value = e.latlng.lat;
        document.getElementById("long").value = e.latlng.lng;
    });
    var intervalId = window.setInterval(function () {
        /// call your function here

        var trafficresponse;
        var obj = null;
        SubmitFormAJAX("start_simulation_form", responseSimulation)
    }, 5000);
}

