// Zero padding
function PrefixInterger(num, n) {
    return (Array(n).join(0) + num).slice(-n);
}

function getTime() {
    var DateString, TimeString;
    var date = new Date();
    TimeString = "";
    // Concat current time
    TimeString = TimeString.concat(PrefixInterger(date.getHours(), 2), ":", PrefixInterger(date.getMinutes(), 2), ":", PrefixInterger(date.getSeconds(), 2));
    // modify the value and display
    document.getElementById("Time").innerHTML = TimeString;
    switch (new Date().getDay()) {
        case 0:
            DateString = "Sunday, ";
            break;
        case 1:
            DateString = "Monday, ";
            break;
        case 2:
            DateString = "Tuesday, ";
            break;
        case 3:
            DateString = "Wednesday, ";
            break;
        case 4:
            DateString = "Thursday, ";
            break;
        case 5:
            DateString = "Friday, ";
            break;
        case 6:
            DateString = "Saturday, ";
            break;
    }

    // Concat current date
    DateString = DateString.concat(date.getDate(), " ");

    // Concat current month
    switch (new Date().getMonth()) {
        case 0:
            DateString = DateString.concat("January ");
            break;
        case 1:
            DateString = DateString.concat("Febuary ");
            break;
        case 2:
            DateString = DateString.concat("March ");
            break;
        case 3:
            DateString = DateString.concat("April ");
            break;
        case 4:
            DateString = DateString.concat("May ");
            break;
        case 5:
            DateString = DateString.concat("June ");
            break;
        case 6:
            DateString = DateString.concat("July ");
            break;
        case 7:
            DateString = DateString.concat("August ");
            break;
        case 8:
            DateString = DateString.concat("September ");
            break;
        case 9:
            DateString = DateString.concat("Octorber ");
            break;
        case 10:
            DateString = DateString.concat("November ");
            break;
        case 11:
            DateString = DateString.concat("December ");
            break;
    }
    // Concat current year
    DateString = DateString.concat(date.getFullYear());
    // modify the value and display
    document.getElementById("Date").innerHTML = DateString

}

// call the function every 1s.
setInterval("getTime()", 1000);

function ProgressBar() {
    var winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    var height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    var scrolled = (winScroll / height) * 100;
    document.getElementById("Bar").style.width = scrolled + "%";
}

// call the function every time user scrolls
window.onscroll = function () { ProgressBar() };

function navBar() {
    var navbar = document.getElementById("navbar");

    // If the name of the class of navigation bar is "nav" change to responsive
    if (navbar.className === "nav") {
        navbar.className += " responsive";
    }

    // Else change back to normal
    else {
        navbar.className = "nav";
    }
}

// Page Visit count using local storage

if (typeof (Storage) !== "undefined") {
    if (localStorage.visitcount) {
        localStorage.visitcount = Number(localStorage.visitcount) + 1;
    } else {
        localStorage.visitcount = 1;
    }
    document.getElementById("visitcount").innerHTML = localStorage.visitcount + " time(s)";
} else {
    document.getElementById("visitcount").innerHTML = "Sorry, your browser does not support web storage...";
}