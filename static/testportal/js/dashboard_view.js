
$(document).ready(function() {

    // CSRF TOKEN STUFF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');
    
    $('#add-test-button').click(function() {
        alert('Add test functionality not implemented yet... Use upload test cases instead...');
    });

    
    /*
    Double Click Test Name to Edit
    */
    $('.test-case-name-dashboard-cell').dblclick(function() {
        var test_case_id = this.dataset.testCaseId;
        var test_case_name = $(this).parent().data('test-case-name');
        
        $('#update-test-case-loading').show();
        $('#update-test-case-modal-form').hide();
        $('#update-test-case-modal-error').hide();

        $('#update-test-case-modal').modal('toggle');
        $('#update-test-case-modal-lable').text('Update Test Case: ' + test_case_name);
        $('#update-test-case-modal-accept').data('test-test-case-id', test_case_id);
        $('#view-test-case-button').attr('href', '/test-cases/' + test_case_id);

        // Get Current Result
        $.ajax({
            url: '/api/test-cases/' + test_case_id + '/',
            type: "GET",
            data: {},
            headers:{"X-CSRFToken": csrftoken},
            dataType:'json',
            success: function (response) {
                $('#test-case-id').val(response.id);
                $('#test-case-name').val(response.name);
                $('#test-case-test-id').val(response.test_case_id);
                $('#test-case-suite').val(response.suite);
                $('#test-case-status').val(response.status);
                $('#test-case-type').val(response.test_type);


                $.each(response.tags, function(i,e){
                    $("#test-case-tags option[value='" + e + "']").prop("selected", true);
                });

                $('#test-case-categories').val(response.category);
                $('#test-case-subcategories').val(response.subcategory);
                $('#test-plan').val(response.test_plan);
                $('#test-case-steps').val(response.steps);

                $('#update-test-case-modal-loading').hide();
                $('#update-test-case-modal-form').show();
                $('#update-test-case-modal-error').hide();
                
                console.log("It worked", response);
            },
            error: function(error){
                console.log("Something went wrong", error);
            }
        });
    });
    // Update TestCase Accept
    $('#update-test-case-modal-accept').click(function() {
        // From form
        var test_case_id = $('#test-case-id').val();
        var test_case_name = $('#test-case-name').val();

        var tags = new Array();
        $('#test-case-tags > option:selected').each(
            function(i){
                tags[i] = $(this).val();
            });                

        $.ajax({
            url: '/api/test-cases/' + test_case_id + '/',
            type: "PUT",
            data: {
                'name': $('#test-case-name').val(),
                'test_case_id': $('#test-case-test-id').val(),
                'steps': $('#test-case-steps').val(),
                'suite': $('#test-case-suite').val(),
                'tags': tags,
                'category': $('#test-case-categories').val(),
                'subcategory': $('#test-case-subcategories').val(),
                'test_plan': $('#test-plan').val(),
                'status': $('#test-case-status').val(),
                'test_type': $('#test-case-type').val(),
            },
            headers:{"X-CSRFToken": csrftoken},
            dataType:'json',
            success: function (response) {                        
                case_id = $('#test-case-test-id').val();
                case_name = $('#test-case-name').val();
                
                case_cell_id = '#test-case-name-' + case_id;

                $(case_cell_id).text(case_name);

                $('#view-test-case-button').attr('href', '/');
                
                $('#update-test-case-modal').modal('toggle');
            },
            error: function(error){
                alert("Unable to update result. Please see system administrator.");
                console.log("Something went wrong", error);
            }
        });
    });
    
    // Open Modal for Result
    $('.test-result-dashboard-cell').dblclick(function() {
        var result_id = this.dataset.resultId;
        
        $('#update-result-modal-loading').show();
        $('#update-result-modal-form').hide();
        $('#update-result-modal-error').hide();

        var test_case_name = $(this).parent().data('test-case-name');
        
        $('#update-result-modal').modal('toggle');
        $('#update-result-modal-lable').text('Update Result for ' + test_case_name);
        $('#update-result-modal-accept').data('test-result-id', this.dataset.resultId);

        // Get Current Result
        $.ajax({
            url: '/api/test-results/' + result_id + '/',
            type: "GET",
            data: {},
            headers:{"X-CSRFToken": csrftoken},
            dataType:'json',
            success: function (response) {
                var current_user = $('#dashboard-table').data('current-user');

                $('#test-result-id').val(response.id);
                $('#test-result-test-case').val(response.test_case);
                $('#test-result-date').val(response.result_date);
                $('#test-result-status').val(response.result);
                $('#test-result-user').val(current_user);
                $('#test-result-note').val(response.note);
                $('#test-result-duration').val(response.duration);
                $('#test-result-bug-id').val(response.bug_id);
                
                $('#update-result-modal-loading').hide();
                $('#update-result-modal-form').show();
                $('#update-result-modal-error').hide();
            },
            error: function(error){
                $('#update-result-modal-loading').hide();
                $('#update-result-modal-form').hide();
                $('#update-result-modal-error').show();
                console.log("Something went wrong", error);
            }
        });
    })
    // Update Result on save
    $('#update-result-modal-accept').click(function() {
        // From form
        var result_id = $('#test-result-id').val();
        var test_case_id = $('#test-result-test-case').val();
        var note = $('#test-result-note').val();
        var result_date = $('#test-result-date').val();
        var user_id = $('#test-result-user').val();
        var result = $('#test-result-status').val();
        var bug_id = $('#test-result-bug-id').val();

        $.ajax({
            url: '/api/test-results/' + result_id + '/',
            type: "PUT",
            data: {
                'user': user_id,
                'note': note,
                'result_date': result_date,
                'result': result,
                'test_case': test_case_id,
                'bug_id': bug_id
            },
            headers:{"X-CSRFToken": csrftoken},
            dataType:'json',
            success: function (response) {
                // Update table
                result_id = $('#test-result-id').val();
                result_status = $('#test-result-status').val();
                result_status_text = $('#test-result-status option:selected').text();
                result_cell_id = '#result-cell-id-' + result_id

                var bg_classes = $("#test-result-status option").map(function() {
                    $(result_cell_id).removeClass('bg-' + this.value);
                });
                
                $(result_cell_id).addClass('bg-' + result_status);
                $(result_cell_id).text(result_status_text);

                $('#update-result-modal').modal('toggle');
            },
            error: function(error){
                alert("Unable to update result. Please see system administrator.");
                console.log("Something went wrong", error);
            }
        });
    });


    $("#test-search-box").on("keyup", function() {
        var value = $(this).val().toLowerCase();
        $("#dashboard-table tr.test-case-row").filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });

    $('#upload-result-modal-accept').click(function() {
        var formData = new FormData($('#upload-result-form')[0]);
        var suiteId = $('#upload-result-button').data('suite-id');

        if ($('#result-file-to-upload').val() == "") {
            $('#upload-error').html('Please select a file...');
            $('#upload-error').show();
            return;
        }

        $.ajax({
            url: '/api/upload/test-results/' + suiteId,
            type: "POST",
            data: formData,
            headers:{
                "X-CSRFToken": csrftoken,
            },
            cache: false,
            contentType: false,
            processData: false,
            success: function (response) {
                $('#upload-error').html('');
                $('#test-case-json-to-upload').val('');
                $('#upload-error').hide();

                if (response.missing_results.length > 0) {
                    alert('The following cases are missing results:\n - ' + response.missing_results.join('\n - '));
                }

                if (response.missing_cases.length > 0) {
                    alert('The following results have no matching case:\n - ' + response.missing_cases.join('\n - '));
                }

                $('#upload-result-modal').modal('toggle');
                location.reload();
            },
            error: function(error){
                $('#upload-error').html(error.responseJSON.error);
                $('#upload-error').show();
                console.log("Something went wrong", error);
            }
        });
    });
});