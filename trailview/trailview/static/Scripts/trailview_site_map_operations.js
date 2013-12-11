var panos;                        // list of all panoramas on this trail
var trailWidePoIs                 // list of all the points of interest that cover the entire trail
var panorama;                     // panorama representing the current view
var usingEntryPano = false;       // indicates whether there is an entry pano (one of google's)
var entryPanoId = null;           // id of entry pano
var initialPano = null;           // the inital pano to display
var trailName = null;             // the trail name
var currentPanoNumber = null;     // the pano number of the current panorama

/**
*  The entry function for this program
*  panos: list of all panoramas for this trail
*  links: list of all links for this trail
*  initalPanoId: the id of the inital pano to display (can, and usually will be, blank)
*/
function begin(panosJson, initialPanoId, trail, twPoIs) {
    try {
        panos = $.parseJSON(panosJson);
        trailWidePoIs = $.parseJSON(twPoIs);
    } catch (ex) {
        alert('Something went wrong!');
        return;
    }
    panos = panos.sort(function (a, b) { return a.PanoNumber - b.PanoNumber; });
    initialPano = initialPanoId != '' && initialPanoId != null ? initialPanoId : null;
    trailName = trail;
    initialize();
}

/**
*  The initializing function for this program
*/
function initialize() {
    // set the entry coordinates to either the entry pano or the first pano
    var entryArea;
    if (panos[0].Name == '_entryPano') {
        usingEntryPano = true;
        entryArea = new google.maps.LatLng(panos[0].LocationLat, panos[0].LocationLng);
    }

    panorama = new google.maps.StreetViewPanorama(document.getElementById('pano_canvas'));
    var panoOptions;
    if (entryArea != null && initialPano == null) {
        panoOptions = {
            position: entryArea,
            addressControl: false,
            visible: true,
            enableCloseButton: false,
            clickToGo: true,
            zoomControlOptions: {
                position: google.maps.ControlPosition.TOP_LEFT,
                style: google.maps.ZoomControlStyle.SMALL
            },
            panoProvider: getCustomPanorama
        };
    } else {
        panoOptions = {
            addressControl: false,
            visible: true,
            enableCloseButton: false,
            clickToGo: true,
            zoomControlOptions: {
                position: google.maps.ControlPosition.TOP_LEFT,
                style: google.maps.ZoomControlStyle.SMALL
            },
            panoProvider: getCustomPanorama
        }
    }
    panorama.setOptions(panoOptions);

    if (usingEntryPano) { // grab the entry pano, if it is being used and add link change listener
        var streetviewService = new google.maps.StreetViewService();
        var radius = 50;
        streetviewService.getPanoramaByLocation(entryArea, radius,
            function (result, status) {
                if (status == google.maps.StreetViewStatus.OK) {
                    google.maps.event.addListener(panorama, 'links_changed',
                      function () {
                          createCustomLinks(result.location.pano);
                      });
                }
            });
    } // else, there is no need for a custom link provider so there is no need for a listener

    // add some other listeners
    google.maps.event.addListener(panorama, 'pano_changed',
        function () {
            var p = $.grep(panos, function (elem, index) {
                return elem.Name == panorama.getPano();
            })[0];

            if (p.PanoNumber < currentPanoNumber) { // going backwards
                panorama.setPov({
                    heading: (((p.InitialHeading - 180) < 0) ?
                        (p.InitialHeading + 180) : (p.InitialHeading - 180)),
                    pitch: panorama.getPov().pitch
                });
            } else { // forwards
                panorama.setPov({
                    heading: p.InitialHeading,
                    pitch: panorama.getPov().pitch
                });
            }

            currentPanoNumber = p.PanoNumber;
            
            updateInfoArea(p.PointsOfInterest.concat(trailWidePoIs));
        });

    // unnecessary for production
    //google.maps.event.addListener(panorama, 'pov_changed',
    //    function () {
    //        updatePanoInfo(panorama);
    //    });

    if (initialPano == null) {
        currentPanoNumber = 0;
        panorama.setPano(panos[0].Name);
    } else {
        currentPanoNumber = $.grep(panos, function (e, i) {
            return e.Name == initialPano;
        })[0].PanoNumber;
        panorama.setPano(initialPano);
    }

    RequestMoreData(0);
}

/**
*  Returns the path to the needed tile
*/
function getCustomPanoramaTileUrl(pano, zoom, tileX, tileY) {
    return '/static/panos/' + trailName + '/' + pano + '/tile_' + zoom + '_' + tileX + '-' + tileY +
        '.png';
}

/**
*  Gets the custom panorama
*  pano: id of the custom panorama
*/
function getCustomPanorama(pano) {
    var p = $.grep(panos, function (e, i, a) {
        return e.Name == pano;
    })[0];
    if (p != null) {
        return {
            location: {
                pano: p.Name,
                description: p.Description,
                latLng: new google.maps.LatLng(p.LocationLat, p.LocationLng)
            },
            links: p.Links,
            tiles: {
                tileSize: new google.maps.Size(p.TileWidth, p.TileWidth / 2),
                worldSize: new google.maps.Size(p.ImageWidth, p.ImageWidth / 2),
                centerHeading: p.ForwardHeading,
                getTileUrl: getCustomPanoramaTileUrl
            }
        }
    }
    return null;
}

/**
*  Creates custom links for custom panos and entry pano
*  entryPanoId: id of the potential entry pano
*/
function createCustomLinks(entryPanoId) {
    var links = panorama.getLinks();
    var panoId = panorama.getPano();

    if (typeof links != 'undefined') {
        if (panoId == entryPanoId) {
            for (var i = 0; i < allLinks.length; ++i) {
                if (allLinks[i].IsEntryPano == 'True') {
                    links.push({
                        heading: allLinks[i].Heading,
                        description: allLinks[i].Description,
                        pano: allLinks[i].PanoName
                    });
                }
            }
        } // else: the links object in the panorama class will take care of it
    }
}

/**
* Requests a new chunk of panorama data from the server
*/
function RequestMoreData(num) {
    $.post(sRequestMoreData, { trailName: trailName, num: num }, HandleNewData, 'json');
}

/**
* Handles the callback from the request for more data
* Adds the new panoramas to the list (and sorts it),
* and then initiates another request for more data if necessary
*/
function HandleNewData(data) {
    data.panos.forEach(function (e, i, a) {
        panos.push(e);
    });
    panos = panos.sort(function (a, b) {
        return a.PanoNumber - b.PanoNumber;
    });
    if (data.next != -1) {
        RequestMoreData(data.next);
    }
}