
// get the video player element and initialize the close timer
const videoPlayer = document.querySelector(".video-player");
let closeTimer;
let lastPlaybackTime = 0;
let correctingSeek = false;


async function initializeButtons() {
    const response = await fetch("/config.json");
    if (!response.ok) {
        throw new Error(`Could not load config.json (${response.status}).`);
    }

    const config = await response.json();
    if (!Array.isArray(config.buttons)) {
        throw new Error("config.json must contain a buttons array.");
    }

    const buttonGrid = document.querySelector(".button-grid");
    const buttons = config.buttons.map((settings, index) => {
        if (typeof settings.label !== "string" ||
            typeof settings.class !== "string" ||
            typeof settings.video !== "string") {
            throw new Error(`Button configuration at index ${index} is incomplete.`);
        }

        const button = document.createElement("button");
        button.type = "button";
        button.className = settings.class;
        button.dataset.video = settings.video;

        if (settings.label_class) {
            if (typeof settings.label_class !== "string") {
                throw new Error(`'label_class' for button ${index} must be a string.`);
            }
            const label = document.createElement("span");
            label.className = settings.label_class;
            label.textContent = settings.label;
            button.append(label);
        } else {
            button.textContent = settings.label;
        }

        buttonGrid.insertBefore(button, videoPlayer);
        return button;
    });

    return buttons;
}

async function checkVideoAvailability(buttons) {
    await Promise.all(buttons.map(async (button) => {
        button.dataset.videoAvailable = "checking";
        try {
            const response = await fetch(button.dataset.video, { method: "HEAD" });
            if (response.ok) {
                button.dataset.videoAvailable = "true";
            } else {
                button.dataset.videoAvailable = "false";
                button.append(" (Video missing)");
            }
        } catch (error) {
            button.dataset.videoAvailable = "false";
            button.append(" (Video missing)");
            console.error(`Could not check video for ${button.textContent}.`, error);
        }
    }));
}


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
async function attachButtonHandlers() {
    const buttons = await initializeButtons();
    await checkVideoAvailability(buttons);

    buttons.forEach((button) => {
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
}

attachButtonHandlers().catch((error) => {
    console.error("Could not initialize video buttons.", error);
    const errorMessage = document.createElement("p");
    errorMessage.setAttribute("role", "alert");
    errorMessage.textContent = "Could not load the video buttons. Check config.json and the server.";
    document.querySelector(".button-grid").prepend(errorMessage);
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
