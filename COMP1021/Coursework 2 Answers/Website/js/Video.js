function videoControl() {
    var video = document.getElementById("video");

    // If the video is paused play instead
    if (video.paused) {
        document.getElementById("videobtn").innerHTML = "&#10073;&#10073;"
        video.play();
    }

    // Otherwise pause
    else {
        document.getElementById("videobtn").innerHTML = "&#9654;"
        video.pause();
    }
}