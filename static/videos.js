videos = get_videos();
hide_all_but_first('video-wrapper');
let current_video = 0;


function get_videos() {
    return document.getElementById('video-wrapper').children;
}

function changePlayer(direction) {
    //hide current player
    videos[current_video].classList.add('hide');

    //stop video playing
    let src = videos[current_video].getAttribute('src');
    videos[current_video].removeAttribute("src");
    videos[current_video].setAttribute("src", src);

    //find next player
    if (direction === 'r') {
        current_video++;
        current_video %= videos.length;
    } else if (direction === 'l') {
        current_video--;
        if (current_video < 0) {
            current_video = videos.length - 1;
        }
    }

    //show next player
    videos[current_video].classList.remove('hide');
}


function hide_all_but_first(parent) {
    //TODO: connect this and identical in music.js
    let musicWrap = document.getElementById(parent);
    let children = musicWrap.children;

    if (musicWrap.childElementCount <= 1) {
        let arrows = document.getElementsByClassName('arrow');
        for (let i = 0; i < arrows.length; i++) {
            arrows[i].classList.add('hide');
        }
        return;
    }

    for (let i = 1; i < musicWrap.childElementCount; i++) {
        children[i].classList.add('hide');
    }
}