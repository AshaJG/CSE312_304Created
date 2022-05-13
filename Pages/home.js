// Establish a WebSocket connection with the server
const socket = new WebSocket('ws://' + window.location.host + '/websocket');

function sendLike(post_id){

    socket.send(JSON.stringify({'post_ID':post_id,'like':0}));
}

//needs a function to display it back on the website
function start(like_dict) {
    let chat = document.getElementById(like_dict.post_ID);
    chat.innerHTML = like_dict.like + " like";
}
socket.onmessage = function (ws_message) {
    const message = JSON.parse(ws_message.data);
    console.log(message)
    start(message)
}

function checkInfo(event){
    let username = document.getElementById("username").value
    let password = document.getElementById("password").value
    if (username.includes('/') || username.includes('\\')){
        event.preventDefault();
        document.getElementById("username_error").style.display = "inline-block";
    }
    if (password.length <= 5){
        event.preventDefault();
        document.getElementById("password_error").style.display = "inline-block";
    }
}
