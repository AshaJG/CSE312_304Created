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