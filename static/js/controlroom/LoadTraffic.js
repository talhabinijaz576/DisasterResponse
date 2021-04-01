function responseSimulation(obj) {
    console.log("got the response");
    var inimarkers = [];
    if (obj.status == "ok") {

        // alert(obj.routes[0].previousLocation);
        if (obj.routes[0].previousLocation == null) {

            for (i = 0; i < obj.routes.length; i++) {
                if(obj.routes[i].type != "Policecar")
                    var initialmarker = L.marker(obj.routes[i].currentLocation, { icon: greenIcon }).addTo(mymap);
                else var initialmarker = L.marker(obj.routes[i].currentLocation, { icon: fire }).addTo(mymap);
                inimarkers.push(initialmarker);
            }
            setTimeout(
                function () {
                    for (i = 0; i < inimarkers.length; i++) {
                        mymap.removeLayer(inimarkers[i]);
                    }
                }, 5000);

        }

        else {
            var markers = [];
            for (i = 0; i < obj.routes.length; i++) {
                var line = L.polyline([obj.routes[i].previousLocation, obj.routes[i].currentLocation]);
                if(obj.routes[i].type != "Policecar")
                    var animatedMarker = L.animatedMarker(line.getLatLngs(), { icon: greenIcon });
                else var animatedMarker = L.animatedMarker(line.getLatLngs(), { icon: fire });
                mymap.addLayer(animatedMarker);
                markers.push(animatedMarker);
            }

            setTimeout(
                function () {
                    for (i = 0; i < markers.length; i++) {
                        mymap.removeLayer(markers[i]);
                    }
                }, 5000);
        }
    }
}