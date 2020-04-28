var map;
function getUserLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(getUserLatLon);
    } else {
        alert("Geolocation not available");
    }
}

function getUserLatLon(position) {
    var lat = position.coords.latitude;
    var lon = position.coords.longitude;
    initMap(lat, lon);
}

function initMap(lat, lon) {

    var y = document.getElementById("googleMap");

    y.style.border = "1px solid black";

    var userLocation = new google.maps.LatLng(lat, lon);
    var Nanjing = new google.maps.LatLng(32.047545, 118.79120);
    var LZU = new google.maps.LatLng(35.945108, 104.157322);
    var Leeds = new google.maps.LatLng(53.807162, -1.555172);
    var mapCanvas = document.getElementById("googleMap");

    var mapOptions = { center: LZU, zoom: 2, disableDefaultUI: false };

    map = new google.maps.Map(mapCanvas, mapOptions);

    var markerOne = new google.maps.Marker({ position: userLocation });
    markerOne.setMap(map);

    var markerTwo = new google.maps.Marker({ position: Nanjing });
    markerTwo.setMap(map);

    var markerThree = new google.maps.Marker({ position: LZU });
    markerThree.setMap(map);

    var markerFour = new google.maps.Marker({ position: Leeds });
    markerFour.setMap(map);

    var infowindowOne = new google.maps.InfoWindow({
        content: "You are here"
    });

    var infowindowTwo = new google.maps.InfoWindow({
        content: "This is my hometown"
    });

    var infowindowThree = new google.maps.InfoWindow({
        content: "This is Lanzhou University"
    });

    var infowindowFour = new google.maps.InfoWindow({
        content: "This is University of Leeds"
    });

    google.maps.event.addListener(markerOne, 'click', function () {
        infowindowOne.open(map, markerOne);
        var pos = map.getZoom();
        map.setZoom(9);
        map.setCenter(userLocation);
        window.setTimeout(function () { map.setZoom(pos); }, 4000);
    });

    google.maps.event.addListener(markerTwo, 'click', function () {
        infowindowTwo.open(map, markerTwo);
        var pos = map.getZoom();
        map.setZoom(9);
        map.setCenter(geneva);
        window.setTimeout(function () { map.setZoom(pos); }, 4000);
    });

    google.maps.event.addListener(markerThree, 'click', function () {
        infowindowThree.open(map, markerThree);
        var pos = map.getZoom();
        map.setZoom(9);
        map.setCenter(geneva);
        window.setTimeout(function () { map.setZoom(pos); }, 4000);
    });

    google.maps.event.addListener(markerFour, 'click', function () {
        infowindowFour.open(map, markerFour);
        var pos = map.getZoom();
        map.setZoom(9);
        map.setCenter(geneva);
        window.setTimeout(function () { map.setZoom(pos); }, 4000);
    });
}

function changeMapSat(map) {
    map.setMapTypeId(google.maps.MapTypeId.HYBRID);
}

function changeMapTerrain(map) {
    map.setMapTypeId(google.maps.MapTypeId.TERRAIN);
}

function changeMapRoad(map) {
    map.setMapTypeId(google.maps.MapTypeId.ROADMAP);
}

function changeZoom(map, x) {
    var newZoom = map.getZoom() + x;
    map.setZoom(newZoom);
}  