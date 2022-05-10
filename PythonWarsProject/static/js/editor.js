function mx_showPopup(){
    $("#mx_popup_conainer").css("display", "flex");
    $("#mx_popup_conainer").animate({"opacity": 1});
}

function mx_hidePopup(){
    $("#mx_popup_conainer").animate({"opacity": 0}, () => {
        $("#mx_popup_conainer").css("display", "none");
    });
}

function mx_saveCSS(){
    document.getElementsByName("mx_style_file_content")[0].value = editor.getValue();
    mx_showPopup();
    $("#css_editor").ajaxSubmit({
        method: 'POST',
        url: '/wp-content/plugins/matrix/includes/admin/mx_admin_ajax.php',
        success: (response) => {
            console.log(response)
            if(response['error'] != undefined){
                $("#mx_popup__header_text")[0].textContent = "Ошибка: " + response['error'];
            }
            else{
                mx_hidePopup();
            }
        }
    });
}