// img_gen.js
var form_image = document.getElementById('form_images')
var IdImg = document.getElementById('idImg')

form_image.addEventListener('submit', function (event) {
    event.preventDefault()

    var width = document.getElementById('width').value
    var height = document.getElementById('height').value
    var gray = document.getElementById('gray').checked
    var blur = document.getElementById('range_blur').value

    // ID Imagens vão de 0->1084
    var numeroAleatorio = Math.floor(Math.random() * 1085);
    IdImg.textContent = "ID: " + numeroAleatorio;
    IdImg.style.marginTop = "150px";

    var url = `https://picsum.photos/id/${numeroAleatorio}/${width}/${height}`
    var url_gray = `https://picsum.photos/id/${numeroAleatorio}/${width}/${height}?grayscale`
    var url_blur = `https://picsum.photos/id/${numeroAleatorio}/${width}/${height}?blur=${blur}`
    var url_bg = `https://picsum.photos/id/${numeroAleatorio}/${width}/${height}?grayscale&blur=${blur}`

    var image = document.getElementById('img')

    if (gray == true && blur >= 1) {
        image.src = url_bg
    } else if (gray == true) {
        image.src = url_gray
    } else if (blur >= 1) {
        image.src = url_blur
    } else {
        image.src = url
    }

})