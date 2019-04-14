/*
    dynaswap.js - Utility functions for both register and authenticate

    dependent on jquery
*/
var DynaSwap = {

    ifOkStartCamera() {
        let userName = $("#userName").val().trim();
        let role = $("#selectedRole").val();
        if (userName.length == 0)
        {
            $("#userNameRoleMessage").text("Please enter a Username");
            $("#userNameRoleMessage").show();
            return;
        }

        $.get("/get_user_role/", { "userName": userName, "role": role }).then(
            function(data) {
                if (data["status"] === "success") {
                    $("#userNameRoleMessage").hide();
                    $("#userId").val(data["user_id"]);

                    // Start camera
                    utils.clearError();
                    utils.startCamera('qvga', onVideoStarted, 'videoInput');

                    snapButton.style.visibility = "visible";
                    caption1.style.visibility = "visible";
                }
                else if (data["status"] === "already_registered") {
                    $("#userNameRoleMessage").text("Username/Role combination already registered");
                    $("#userNameRoleMessage").show();
                }                
                else if (data["status"] === "not_registered") {
                    $("#userNameRoleMessage").text("Username/Role combination not yet registered");
                    $("#userNameRoleMessage").show();
                }
                else if (data["status"] === "unknown") {
                    $("#userNameRoleMessage").text("Unknown Username/Role combination");
                    $("#userNameRoleMessage").show();
                }
                else {
                    console.log(data["error"]);
                    alert('Sorry an unexpected error has occurred, please try again');
                }
            },
            function(error) {
                console.log(error);
                alert('Sorry an unexpected error has occurred, please try again');
            }
        );
    }    
};
