/**
 Hides the Div containing the max_slots Field when creating or editing a Course as an admin
 if checkbox for unlimited number of participants is checked
 and sets the value of max_slots=9999.
 The Div reappears when checkbox is unchecked.
 */
window.addEventListener("load", function () {
    (function () {
        if (location.href.lastIndexOf("change") === -1)
            return;
        let showAttribute = true;
        let label = document.getElementsByClassName("form-row field-max_slots")[0].getElementsByClassName("required")[0];
        let min_GroupSize = document.getElementsByClassName('form-row field-min_slot_size')[0];
        let max_GroupSize = document.getElementsByClassName('form-row field-max_slot_size')[0];

        django.jQuery(document).ready(function () {
            if (django.jQuery('#id_groupTopic').is(':checked')) {

                min_GroupSize.style.display = 'flex';
                max_GroupSize.style.display = 'flex';
                label.innerText = 'Maximale Gruppenanzahl';
                showAttribute = false;
            } else {
                min_GroupSize.style.display = 'none';
                max_GroupSize.style.display = 'none';
                label.innerText = 'Maximale Teilnehmeranzahl';
                showAttribute = true;
            }
            django.jQuery("#id_groupTopic").click(function () {
                showAttribute = !showAttribute;
                if (showAttribute) {
                    min_GroupSize.style.display = 'none';
                    max_GroupSize.style.display = 'none';
                    document.getElementById("id_min_slot_size").value = 1;
                    document.getElementById("id_max_slot_size").value = 1;
                    label.innerText = 'Maximale Teilnehmeranzahl';
                } else {
                    min_GroupSize.style.display = 'flex';
                    max_GroupSize.style.display = 'flex';
                    label.innerText = 'Maximale Gruppenanzahl';
                }
            })
        })
    })(django.jQuery);
});