/**
Hides the Div containing the max_participants Field when creating or editing a Course as an admin
if checkbox for unlimited number of participants is checked
and sets the value of max_participants=9999.
The Div reappears when checkbox is unchecked.
*/
window.addEventListener("load", function() {
    (function() {
        showAttribute=true;
        django.jQuery(document).ready(function(){
            if (django.jQuery('#id_unlimited').is(':checked')) {
                document.getElementsByClassName('form-row field-max_participants')[0].style.visibility = 'hidden';
                showAttribute=false;
            } else {
                document.getElementsByClassName('form-row field-max_participants')[0].style.visibility = 'visible';
                showAttribute=true;
            }
            django.jQuery("#id_unlimited").click(function(){
                showAttribute=!showAttribute;
                if (showAttribute) {
                    document.getElementsByClassName('form-row field-max_participants')[0].style.visibility = 'visible';
                } else {
                    document.getElementsByClassName('form-row field-max_participants')[0].style.visibility = 'hidden';
                    document.getElementById("id_max_participants").value = 9999;
                }
            })
        })
    })(django.jQuery);
});