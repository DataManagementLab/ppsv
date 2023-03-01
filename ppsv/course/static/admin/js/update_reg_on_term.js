$(document).ready(function () {
    console.log("Hello world");
    $('#id_term').on('change', function () {
        var term_id = $(this).val();
        $.ajax({
            url: '/admin/course/term/get-term/' + term_id + '/',
            success: function (data) {
                const reg_start = data['reg_start'];
                const date_reg_start = reg_start.split(" ")[0]
                const time_reg_start = reg_start.split(" ")[1].split("+")[0];
                $('#id_registration_start_0').val(date_reg_start);
                $('#id_registration_start_1').val(time_reg_start);
                const reg_end = data['reg_end'];
                const date_reg_end = reg_end.split(" ")[0]
                const time_reg_end = reg_end.split(" ")[1].split("+")[0];
                $('#id_registration_deadline_0').val(date_reg_end);
                $('#id_registration_deadline_1').val(time_reg_end);
            }
        });
    });
});