var disasterMarker = [];
function setCasualtiesValue() {
    document.getElementById("casualtiesvalue").value = document.getElementById("casualties").value;

}
function setCasualtiesSlider() {
    document.getElementById("casualties").value = document.getElementById("casualtiesvalue").value;

}

function setIntensityValue() {
    document.getElementById("intensityvalue").value = document.getElementById("intensity").value;

}
function setIntensitySlider() {
    document.getElementById("intensity").value = document.getElementById("intensityvalue").value;

}

function addDisaster(){
    if(document.getElementById("disaster-type").value == "Select")
    {
        alert("Please select type of the Disaster");
        return false;
    }
    if(document.getElementById("lat").value == 0)
    {
        alert("Please enter latitude and longitude of the Disaster or Click on the location on the map");
        return false;
    }
    if(document.getElementById("long").value == 0)
    {
        alert("Please enter latitude and longitude of the Disaster or Click on the location on the map");
        return false;
    }
    if(document.getElementById("intensityvalue").value == 0)
    {
        alert("Please enter approximate Intensity of the Disaster");
        return false;
    }
    if(document.getElementById("casualtiesvalue").value == 0)
    {
        alert("Please enter approximate Casualties of the Disaster");
        return false;
    }
    var cnfrmmsg = "Please confirm the Disaster Details\n"+document.getElementById("disaster-type").value+" Disaster of Intensity "+document.getElementById("intensityvalue").value+" and Casualties "+document.getElementById("casualtiesvalue").value+ " at location "+ document.getElementById("lat").value +","+document.getElementById("long").value;
    var r = confirm(cnfrmmsg);
    if (r == true)
        SubmitFormAJAX("disaster-data-form", postdisaster);
}

function postdisaster(resp)
{
    if(resp.status == "ok"){
        //var mp = new L.Marker([document.getElementById("lat").value, document.getElementById("long").value], {icon: fire}).addTo(mymap);
        var mp = new L.Marker([document.getElementById("lat").value, document.getElementById("long").value], {icon: cssIcon}).addTo(mymap);
        if(document.getElementById("disaster-type").value == "Fire")
            mp = new L.Marker([document.getElementById("lat").value, document.getElementById("long").value], {icon: cssIcon}).addTo(mymap);
        if(document.getElementById("disaster-type").value == "Flood")
            mp = new L.Marker([document.getElementById("lat").value, document.getElementById("long").value], {icon: cssIconFlood}).addTo(mymap);
        if(document.getElementById("disaster-type").value == "Earthquake")
            mp = new L.Marker([document.getElementById("lat").value, document.getElementById("long").value], {icon: cssIconQuake}).addTo(mymap);
        if(document.getElementById("disaster-type").value == "Accident")
            mp = new L.Marker([document.getElementById("lat").value, document.getElementById("long").value], {icon: cssIconAcc}).addTo(mymap);
        disasterMarker.push(mp);
    }
}