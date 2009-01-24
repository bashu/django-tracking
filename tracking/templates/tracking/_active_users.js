//<![CDATA[
var AUmap;
var markerList = new Array();
var blurbs = new Array();

$(document).ready(function () {
    if (GBrowserIsCompatible()) {
        // set up Google Maps
        origin = new GLatLng(35.232253,-95.273437);
        AUmap = new GMap2(document.getElementById("active-users-map"));
        AUmap.setCenter(origin, 2);
        AUmap.addControl(new GSmallMapControl());
        AUmap.addControl(new GMapTypeControl());
        AUmap.enableScrollWheelZoom();

        // now fetch the active users
        createMarkers();

        // refresh the markers every 5 seconds or so
        setInterval('createMarkers()', 5000);

        $('.active-user h3').live('click', function () {
                var p = $(this).parent().get(0);
                var num = parseInt(p.id.replace('au-', ''));
                var marker = markerList[num];

                AUmap.openInfoWindowHtml(marker.getLatLng(), blurbs[num]);
                AUmap.panTo(marker.getLatLng());
            });
    } else {
        alert('This page requires a modern browser which supports Google Maps!');
    }
});
$(document).unload(GUnload);

function createMarkers() {
    // Pull back all active users and create markers for them
    $.ajax({
        url : '{% url tracking-get-active-users %}',
        type : 'POST',
        dataType : 'json',
        success : function (json) {
            var userList = $('#active-users-list');

            $.each(json.users, function (i, user) {
                    var url = '<a href="' + user.url + '">' + user.url + '</a>';
                    if (!markerList[user.id] && user.geoip && user.geoip.city && user.geoip.city != 'None') {
                        // determine which flag to use
                        var img = '<img src="/static/images/flags/' +
                                user.geoip.country_code.toLowerCase() +
                                '.png" class="flag" />';

                        // come up with some HTML to put in the list
                        var listHtml = '<div id="au-' + user.id + '" ' +
                            'class="active-user location-info"><h3>' +
                            user.geoip.city + '</h3><div>' + img +
                            user.geoip.region_name + ', ' +
                            user.geoip.country_name + '</div>' +
                            '<div><strong>Viewing</strong> <span id="auu-' + user.id +'">' +
                            url + '</span></div>' +
                            '<div><strong>Using</strong> ' + user.user_agent + '</div>' +
                            '<div><strong>From</strong> <a href="' + user.referrer + '">' +
                            user.referrer + '</a></div>' +
                            '<div><strong>Updated</strong> <span id="lu-' + user.id + '">' +
                            user.last_update + '</span>' +
                            ' seconds ago</div></div>';
                        userList.prepend(listHtml);

                        // add a marker to the map
                        var point = new GLatLng(user.geoip.latitude,
                                                user.geoip.longitude);

                        AUmap.addOverlay(createMarker(point, user, img));
                    } else {
                        $('#auu-' + user.id).html(url);
                        $('#lu-' + user.id).html(user.last_update);
                    }
                });

            // Clean up old markers
            $.each(markerList, function (i, marker) {
                    if (marker) {
                        var inList = false;
                        $.each(json.users, function (j, juser) {
                                if (i == juser.id) {
                                    inList = true;
                                    return;
                                }
                            });
                        if (!inList) {
                            AUmap.removeOverlay(marker);
                            $('#au-' + i).remove();
                            markerList[i] = null;
                        }
                    }
                });
        }
    });
}

function createMarker(point, user, img) {
    // Add a marker overlay to the map and store various bits of info about it
    var marker = new GMarker(point);
    marker.value = user.id;

    var myHtml = '<div class="mapOverlay"><h3>' + user.geoip.city + '</h3>';
    myHtml += '<div>' + img + user.geoip.region_name;
    myHtml += ', ' + user.geoip.country_name + '</div></div>';

    // Add a listener to pop up an info box when the mouse goes over a marker
    GEvent.addListener(marker, "mouseover", function() {
        AUmap.openInfoWindowHtml(point, myHtml);
    });

    // Keep track of the marker's data
    markerList[user.id] = marker;
    blurbs[user.id] = myHtml;

    return marker;
}
//]]>
