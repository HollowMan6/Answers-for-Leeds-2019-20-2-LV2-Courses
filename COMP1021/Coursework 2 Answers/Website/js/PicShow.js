function changeIndex(x) {
    PicShow(indexOfPic += x);
}

function PicShow(x) {
    var pic = document.getElementsByClassName("Leedspic");
    var i = 0;

    if (x > pic.length - 1) {
        indexOfPic = 0;
    }

    if (x < 0) {
        indexOfPic = pic.length - 1;
    }

    for (i; i < pic.length; i++) {
        pic[i].style.display = "none";
    }
    pic[indexOfPic].style.display = "block";
}

var indexOfPic = 0;

PicShow(indexOfPic);
