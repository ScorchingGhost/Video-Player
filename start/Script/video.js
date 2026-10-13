
// get the video player element and initialize the close timer
const videoPlayer = document.querySelector(".video-player");
let closeTimer;
let lastPlaybackTime = 0;
let correctingSeek = false;


// check the files to see if a viseo is attached to the button assigned to it otherwise add a message to the button
document.querySelectorAll("button[data-video]").forEach(async (button) => {
    button.dataset.videoAvailable = "checking";
    try {
        const response = await fetch(button.dataset.video, { method: "HEAD" });
        if (response.ok) {
            button.dataset.videoAvailable = "true";
        } else {
            button.dataset.videoAvailable = "false";
            button.textContent += " (Video missing)";
        }
    } catch (error) {
        button.dataset.videoAvailable = "false";
        button.textContent += " (Video missing)";
        console.error(`Could not check video for ${button.textContent}.`, error);
    }
});


// closes the video player and resets the video source
async function closeVideo() {
    if (!videoPlayer.ended) {
        return;
    }

    if (document.fullscreenElement === videoPlayer) {
        await document.exitFullscreen().catch(() => {});
    } else if (videoPlayer.webkitDisplayingFullscreen && videoPlayer.webkitExitFullscreen) {
        videoPlayer.webkitExitFullscreen();
    }

    videoPlayer.pause();
    videoPlayer.removeAttribute("src");
    videoPlayer.load();
    videoPlayer.hidden = true;
}


// when button pressed opens video in fullscreen and plays it, if the video is missing it will not play
document.querySelectorAll("button[data-video]").forEach((button) => {
    button.addEventListener("click", () => {
        if (button.dataset.videoAvailable !== "true") {
            return;
        }

        clearTimeout(closeTimer);
        lastPlaybackTime = 0;
        correctingSeek = false;
        videoPlayer.src = button.dataset.video;
        videoPlayer.hidden = false;
        videoPlayer.load();

        if (videoPlayer.requestFullscreen) {
            videoPlayer.requestFullscreen().catch(() => {});
        } else if (videoPlayer.webkitEnterFullscreen) {
            videoPlayer.webkitEnterFullscreen();
        }

        videoPlayer.play().catch(() => {});
    });
});


videoPlayer.addEventListener("timeupdate", () => {
    if (!videoPlayer.seeking && !correctingSeek) {
        lastPlaybackTime = videoPlayer.currentTime;
    }
});

videoPlayer.addEventListener("seeking", () => {
    if (!videoPlayer.hidden && !videoPlayer.ended && !correctingSeek) {
        correctingSeek = true;
        videoPlayer.currentTime = lastPlaybackTime;
    }
});

videoPlayer.addEventListener("seeked", () => {
    if (!videoPlayer.hidden && !videoPlayer.ended &&
        Math.abs(videoPlayer.currentTime - lastPlaybackTime) > 0.25) {
        videoPlayer.currentTime = lastPlaybackTime;
        return;
    }

    correctingSeek = false;
});


// make sure the video cant be paused, if it is paused and not ended it will start playing again.
videoPlayer.addEventListener("pause", () => {
    if (!videoPlayer.hidden && !videoPlayer.ended) {
        videoPlayer.play().catch(() => {});
    }
});


// when the video ends, start a timer to close the video player after 1 second
videoPlayer.addEventListener("ended", () => {
    closeTimer = setTimeout(() => {
        closeTimer = undefined;
        closeVideo();
    }, 1000);
});
