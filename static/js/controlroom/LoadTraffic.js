function responseSimulation(unobj) {
    console.log("got the response");
    var inimarkers = [];
    console.log(unobj.status);
    if (unobj.status == "ok") {

        // alert(obj.routes[0].previousLocation);
        const obj = sortByProperty(unobj.routes, 'routes.currentLocation');
        if (obj[0].previousLocation == null) {
            
            for (i = 0; i < obj.length; i++) {
                if(obj[i].type != "Policecar")
                    var initialmarker = L.marker(obj[i].currentLocation, { icon: greenIcon }).addTo(mymap);
                else var initialmarker = L.marker(obj[i].currentLocation, { icon: fire }).addTo(mymap);
                initialmarker.bindPopup("trial");
                inimarkers.push(initialmarker);
            }
            var count = 0;
            var arrCount = [];
            for (i = 0; i < inimarkers.length-1; i++){
                if(inimarkers[i].getLatLng() == inimarkers[i+1].getLatLng())
                {
                    count++;
                    arrCount.push(inimarkers[i]);
                }
                else {
                    for(j = 0; j < arrCount.length; j++){
                        arrCount[i].bindPopup(count);
                    }
                    count = 0;
                    arrCount = [];
                }
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
            var count = 1;
            var arrCount = [];
            for (i = 0; i < obj.length; i++) {
                var line = L.polyline([obj[i].previousLocation, obj[i].currentLocation]);
                if(obj[i].type == "Policecar")
                    var animatedMarker = L.animatedMarker(line.getLatLngs(), { icon: police });
                else if(obj[i].type == "Ambulance")
                    var animatedMarker = L.animatedMarker(line.getLatLngs(), { icon: amb });
                else if(obj[i].type == "FireTruck")
                    var animatedMarker = L.animatedMarker(line.getLatLngs(), { icon: fire });
                else 
                    var animatedMarker = L.animatedMarker(line.getLatLngs(), { icon: greenIcon });
                if(i > 0)
                {
                    
                    if(obj[i].currentLocation[0] == obj[i-1].currentLocation[0] && obj[i].currentLocation[1] == obj[i-1].currentLocation[1])
                    {
                        count++;
                        var popupM = "Number of Vehicle: "+count;
                        animatedMarker.bindPopup(String(popupM));
                    }
                    else {
                        count = 0;
                        arrCount = [];
                    }
                }
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

        if(unobj.disaster[0].coordinates != null){
            for(i = 0; i < disasterMarker.length; i++){
                mymap.removeLayer(disasterMarker[i]);
            }
            for(i = 0; i < unobj.disaster.length; i++){
                if(unobj.disaster[i].timeRemaining < 0){
                    continue;
                }
                if(unobj.disaster[i].type != "Accident"){
                    var rad = 100;
                    if(unobj.disaster[i].severity == "easy")
                        rad = 75;
                    if(unobj.disaster[i].severity == "medium")
                        rad = 100;
                    if(unobj.disaster[i].severity == "hard")
                        rad = 125;
                    
                    var Dcolor = "red";
                    var DfillColor = "#f00";

                    if(unobj.disaster[i].type == "Fire"){
                        var Dcolor = "red";
                        var DfillColor = "#f00";
                    }
                    if(unobj.disaster[i].type == "Flood"){
                        var Dcolor = "blue";
                        var DfillColor = "#00f";
                    }
                    if(unobj.disaster[i].type == "Earthquake"){
                        var Dcolor = "black";
                        var DfillColor = "#222";
                    }
                    


                    var circle = L.circle(unobj.disaster[i].coordinates, {
                        color: Dcolor,
                        fillColor: DfillColor,
                        fillOpacity: 0.35,
                        radius: rad
                    }).addTo(mymap);
                    var timeRemain = Math.round(unobj.disaster[i].timeRemaining * 100) / 100
                    circle.bindPopup("<b>"+unobj.disaster[i].type+" Disaster</b><br>Severity: "+unobj.disaster[i].severity+"<br>Time Remaining: "+timeRemain);
                    disasterMarker.push(circle);
                }
                else {
                    var acc = new L.Marker([document.getElementById("lat").value, document.getElementById("long").value], {icon: cssIconAcc}).addTo(mymap);
                    var timeRemain = Math.round(unobj.disaster[i].timeRemaining * 100) / 100
                    acc.bindPopup("<b>"+unobj.disaster[i].type+" Disaster</b><br>Severity: "+unobj.disaster[i].severity+"<br>Time Remaining: "+timeRemain);
                    disasterMarker.push(acc);
                }

            }
        }
    }
}

function sortByProperty(objArray, prop, direction){
    if (!Array.isArray(objArray)) throw new Error("FIRST ARGUMENT NOT AN ARRAY");
   const clone = objArray.slice(0);
    const direct = arguments.length>2 ? arguments[2] : 1; //Default to ascending
    const propPath = (prop.constructor===Array) ? prop : prop.split(".");
    clone.sort(function(a,b){
        for (let p in propPath){
                if (a[propPath[p]] && b[propPath[p]]){
                    a = a[propPath[p]];
                    b = b[propPath[p]];
                }
        }
        // convert numeric strings to integers
        a = String(a).match(/^\d+$/) ? +a : a;
        b = String(b).match(/^\d+$/) ? +b : b;
        return ( (a < b) ? -1*direct : ((a > b) ? 1*direct : 0) );
    });
    
    return clone;
}