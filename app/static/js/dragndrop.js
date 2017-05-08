function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("bookmark_id", ev.target.id);
}

function drop(ev) {
    ev.preventDefault();
    //var data = ev.dataTransfer.getData("bookmark_id");
    window.alert("hola");
    //ev.target.appendChild(document.getElementById(data));
}

window.alert("sii");
