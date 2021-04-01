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
    SubmitFormAJAX("disaster-data-form", postdisaster);
}

function postdisaster(resp)
{
    if(resp.status == "ok"){
        //var mp = new L.Marker([document.getElementById("lat").value, document.getElementById("long").value], {icon: fire}).addTo(mymap);
        var mp = new L.Marker([document.getElementById("lat").value, document.getElementById("long").value], {icon: cssIcon}).addTo(mymap);
    }
}