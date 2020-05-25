/**
 * JS Client-sided form validation
 */
$(document).ready(function() {
    $( "#username" ).blur(function() {
        console.log("Username field blurred")
        username();
    });
    $( "#username" ).focus(function() {
        previouslyFocused = true;
        console.log("Username field has been focused")
    });
    $( "#email" ).keyup(function() {
        email();
    });
    $( "#password" ).keyup(function() {
        password();
    });
    $( "#password2" ).keyup(function() {
        password2();
    });
});

/**
 * Form username AJAX
 */
var previouslyFocused = false;
function username(){
    if (previouslyFocused) {
        var usernameSubmitted = $( "#username" ).val();
        var url = ""; //AJAX request URL
        
        console.log("Looking up whether username "+usernameSubmitted+" is pre-existing via AJAX")
        $.getJSON($SCRIPT_ROOT + '/_check_username', {
            username: usernameSubmitted
        }, function(data) {
            if(data.exists) {
                console.log("User already exists");
                $("#errorusername").text("User name has been used.");
            } else {
                console.log("User does not exist");
                $("#errorusername").text("");
            }
        });
    }
}

/**
 * Form email address format checking
 */
function email(){
    var emailSubmitted = $( "#email" ).val();
    var check = new RegExp('^[a-z0-9.]+@[a-z0-9.-]+\\.[a-z]{2,}$');
    var error = $("#erroremail")
    if (check.test(emailSubmitted)) {
        error.css("color","green");
        error.html("Email is valid");
    }
    else {
        error.css("color","red");
        error.html("Invalid email address.");
    }
    return;
}

/**
 * Form password checking
 */
function password(){
    return
}

/**
 * Form password2 checking
 */
function password2(){
    console.log($( "#password" ).val())
    console.log($( "#password2" ).val())
    var error = $("#errorpassword2")
    if($( "#password" ).val() == $( "#password2" ).val()){
        error.css("color","green");
        error.html("");
    }
    else {
        error.css("color","red");
        error.html("Field must be equal to password");

    }
    return
}