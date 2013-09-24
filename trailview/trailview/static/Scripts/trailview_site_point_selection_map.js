var map;
var markers;
google.maps.visualRefresh = true;

function initializeSelectionMap() {
    markers = [];
    var mapOptions = {
        zoom: 12,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        streetViewControl: false,
        zoomControlOptions: { style: google.maps.ZoomControlStyle.SMALL },
        center: new google.maps.LatLng(44.345089567522514, -68.29243742703858)
    };

    map = new google.maps.Map(document.getElementById('mapPointSelectionCanvas'), mapOptions);
}

function handleDropDownValueChange() {
    if (typeof markers == 'undefined' || markers.length == 0) {
        return;
    }
    requestPointInformation(markers[0].trailId);
}

function requestPointInformation(trailId) {
    markers.forEach(function (e, i, a) {
        e.setMap(null);
    });
    markers.length = 0;

    $.post(GetPossibleEntryPoints, { trailId: trailId, filter: $('#cbPointsFilter').val() }, handlePointInformation, 'json');
}

function handlePointInformation(data) {
    data = data.sort(function (a, b) {
        return a.orderOfMarkers - b.orderOfMarkers;
    });
    map.setCenter(new google.maps.LatLng(data[0].LocationLat, data[0].LocationLng));
    map.setZoom(16);

    for (var i = 0; i < data.length; ++i) {
        var marker = new google.maps.Marker({
            position: new google.maps.LatLng(data[i].LocationLat, data[i].LocationLng),
            map: map,
            trailId: data[i].TrailId,
            panoId: data[i].PanoId,
            title: data[i].Title
        });

        google.maps.event.addListener(marker, 'click', function () {
            window.location.href = (window.location.origin + MapView + '/' + this.trailId + '/' + this.panoId);
        });

        markers.push(marker);
    }
}