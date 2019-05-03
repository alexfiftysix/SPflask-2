let current_player = 0;

bandcamp_players = get_players();
hide_all_but_first('music-wrapper');

/**
 * Get all bandCamp players
 * @returns {HTMLCollection}
 */
function get_players() {
    return document.getElementById('music-wrapper').children;
}

function changeMusicPlayer(direction) {

    //stop music playing
    let src = bandcamp_players[current_player].getAttribute('src');
    bandcamp_players[current_player].removeAttribute("src");
    bandcamp_players[current_player].setAttribute("src", src);

    //hide current player
    bandcamp_players[current_player].classList.add('hide');

    //find next player
    if (direction === 'r') {
        current_player++;
        current_player %= bandcamp_players.length;
    } else if (direction === 'l') {
        current_player--;
        if (current_player < 0) {
            current_player = bandcamp_players.length - 1;
        }
    }

    //show next player
    bandcamp_players[current_player].classList.remove('hide');
}

/**
 * Hide all iframes except the first one
 */
function hide_all_but_first(parent) {
    //TODO: connect this and identical in videos.js
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
