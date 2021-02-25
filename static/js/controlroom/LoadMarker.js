var LeafIcon = L.Icon.extend({
    options: {
        iconSize: [10, 10],
        shadowSize: [0, 0],
        iconAnchor: [0, 0],
        shadowAnchor: [0, 0],
        popupAnchor: [-3, -76]
    }
});

var DisasterIcon = L.Icon.extend({
    options: {
        iconSize: [20, 20],
        shadowSize: [0, 0],
        iconAnchor: [0, 0],
        shadowAnchor: [0, 0],
        popupAnchor: [-3, -76]
    }
});


var earthquake = new LeafIcon({ iconUrl: 'earthquake.jpg' });
var flood = new LeafIcon({ iconUrl: 'flood.png' });
var tsunami = new LeafIcon({ iconUrl: 'tsunami.jpg' });
L.icon = function (options) {
    return new L.Icon(options);
};