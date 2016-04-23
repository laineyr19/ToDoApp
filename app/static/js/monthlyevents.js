var firstpage = true;
var calendar;
function receivingevents(begindate, enddate) {
    $.ajax({
        url : 'http://127.0.0.1:5000/getevents',
        type : 'get',
        data : {
            begindate : begindate,
            enddate : enddate,
        },
        success : function(data) {
            displayeventdata(data);
        }
    });
}
var d = new Date();
var begindate = d.getFullYear() + '/' + (d.getMonth() + 1) + '/' + '01';
var enddate = d.getFullYear() + '/' + (d.getMonth() + 2) + '/' + '01';
receivingevents(begindate, enddate);

function displayeventdata(data) {
    var storeevents = "";
    for (var i = 0; i < data.data.length; i++) {
        var info = data.data[i];
        console.log(info, info.description, info.title, info.starttime, info.endtime, info.categoryid, info.eventid);
        var eventcontent = $("#eventcontent").html();
        var eventdetails = eventcontent
        .replace('{title}', info.title)
        .replace('{description}', info.description)
        .replace('{starttime}', info.starttime)
        .replace('{endtime}', info.endtime)
        .replace('{eventid}', info.id);
        storeevents = "<hr>" + eventdetails + storeevents;

    }
    storeevents = storeevents + "<hr>";
    console.log(storeevents);
    $("#calendarevents").html(storeevents);
}