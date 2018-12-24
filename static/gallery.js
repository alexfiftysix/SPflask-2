gallery_image_path = 'static/images/gallery/';
photos = ['ben_monster.jpg', 'band_monster.jpg', 'ben_floor.jpg', 'guitar_closeup.jpg', 'mojo_heat.jpg', 'sacrifice_crowd.jpg'];
// TODO: alt text

let current_photo = 0;

preload();

function changePhoto(direction) {
    if (direction === 'r') {
        current_photo++;
        current_photo %= photos.length;
    } else if (direction === 'l') {
        current_photo--;
        if (current_photo < 0) {
            current_photo = photos.length - 1;
        }
    }

    document.getElementById('gallery_img').src = gallery_image_path + photos[current_photo];
}

function preload() {
    let prev = current_photo - 1;
    if (prev < 0) {
        prev = photos.length-1;
    }
    let next = (current_photo + 1) % photos.length;

    document.getElementById('previous_photo').src = gallery_image_path + photos[prev];
    document.getElementById('next_photo').src = gallery_image_path + photos[next];
}
