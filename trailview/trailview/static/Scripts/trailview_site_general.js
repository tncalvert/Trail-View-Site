/**
 * General functions used in the operation the trail view site
 *
 */

function intialize() {
    // main display
    $('#close_display').text('Close Display');
    $('#close_display').click(function () { toggleDisplayArea(); });
}

// main display
function toggleDisplayArea() {
    $('#info_area').slideToggle(400, function () {
        if ($('#close_display').text() == 'Close Display') {
            $('#close_display').text('Open Display');
        } else {
            $('#close_display').text('Close Display');
        }
    });
}

// trail list
function toggleTrailDisplayArea(trailId) {
    $('#trail_points_list_' + trailId).slideToggle();
    if ($('#close_trail_points_list_' + trailId).text() == '+') {
        $('#close_trail_points_list_' + trailId).text('-');
    } else {
        $('#close_trail_points_list_' + trailId).text('+');
    }
}

// This is tied into the info area that is commented out in _MapInfoArea.cshtml
//function updatePanoInfo(panorama) {
//    if (typeof panorama != 'undefined' &&
//        typeof panorama.position != 'undefined' &&
//        typeof panorama.pov != 'undefined') {
//        $('#pos_cell').html('(' + panorama.position.lat() +
//                              ', ' + panorama.position.lng() + ')');
//        $('#heading_cell').html(panorama.pov.heading);
//        $('#pitch_cell').html(panorama.pov.pitch);
//        var linksTable = document.getElementById('links_table');
//        while (linksTable.hasChildNodes()) {
//            linksTable.removeChild(linksTable.lastChild);
//        }
//        for (var l in panorama.links) {
//            var row = document.createElement('tr');
//            linksTable.appendChild(row);
//            var labelCell = document.createElement('td');
//            labelCell.innerHTML = '<b>Link: ' + l + '</b>';
//            var valueCell = document.createElement('td');
//            valueCell.innerHTML = panorama.links[l].description;
//            linksTable.appendChild(labelCell);
//            linksTable.appendChild(valueCell);
//        }
//    }
//}

function updateInfoArea(allObjects) {
    for (var i = 0; i <= 3; ++i) {
        updateSingleInfoArea(i, $.grep(allObjects,
            function (e, j) {
                return e.Category == i;
            }));
    }

    var divElems = ['#weather-atmospheric', '#fauna', '#flora', '#points-of-interest'];
    for (var i = 0; i <= divElems.length; ++i) {
        if ($(divElems[i]).text() == '') {
            var contents = '<p>Nothing here for this panorama. Keep moving to find something else.</p>';
            switch (i) {
                case 0:
                    contents += '<a href="' + sPointsOfInterestAtmo + '">Click here to see all the Atmospherics</a>';
                    break;
                case 1:
                    contents += '<a href="' + sPointsOfInterestFau + '">Click here to see all the Fauna</a>';
                    break;
                case 2:
                    contents += '<a href="' + sPointsOfInterestFlo + '">Click here to see all the Flora</a>';
                    break;
                case 3:
                    contents += '<a href="' + sPointsOfInterestLan + '">Click here to see all the Landmarks</a>';
                    break;
            }
            $(divElems[i]).html(contents);
        }
    }
}

function updateSingleInfoArea(cat, obj) {

    var divElems = ['#weather-atmospheric', '#fauna', '#flora', '#points-of-interest'];

    var contents = '';
    obj.forEach(function (e, i, a) {
        contents += '<h4>' + e.Name + '</h4>';
        contents += '<h5>' + e.Description + '  '; // closes after span
        contents += '<span id="seePoI" onclick="$.post(sRequestPoI, { poi_name: &quot;' + e.Name + '&quot;, pano_num: ' + currentPanoNumber + ' }, openInfoItemOverlay, &quot;json&quot;)">Click to see more</span></h5>';
    });
    
    if (obj.length != 0) {
        switch (cat) {
            case 0:
                contents += '<a href="' + sPointsOfInterestAtmo + '">Click here to see all the Atmospherics</a>';
                break;
            case 1:
                contents += '<a href="' + sPointsOfInterestFau + '">Click here to see all the Fauna</a>';
                break;
            case 2:
                contents += '<a href="' + sPointsOfInterestFlo + '">Click here to see all the Flora</a>';
                break;
            case 3:
                contents += '<a href="' + sPointsOfInterestLan + '">Click here to see all the Landmarks</a>';
                break;
        }
    }

    $(divElems[cat]).html(contents);
}

function openInfoItemOverlay(obj) {
    $('#poiInfoPopup').dialog('option', 'title', obj.Name);
    var content = '';
    if (obj.Photo != null)
        content += '<img src="/static/points_of_interest/Photos/' + obj.Photo + '" />';
    if(obj.Description != null)
        content += '<p>' + obj.Description + '</p>';
    if(obj.Audio != null)
        content += '<audio controls="controls">Sorry, your browser does not support embedded HTML5 audio.<source src="/static/points_of_interest/Audio/' + obj.Audio + '.ogg" type="audio/ogg"/><source src="/static/points_of_interest/Audio/' + obj.Audio + '.mp3" type="audio/mp3"/></audio>';
    $('#poiInfoPopup').html(content);
    $('#poiInfoPopup').dialog('open');
}

$(document).ready(function () { intialize(); });
