
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
                $(result_cell_id).removeClass('bg-bug');

                $(result_cell_id).html('');
                $(result_cell_id).prop('title', response.note);
                
                if (response.bug_id != '') {
                    $(result_cell_id).addClass('bg-bug');
                    var bug_url = `https://bugs.aquaveo.com/view.php?id=${response.bug_id}`;
                    $(result_cell_id).html(`<a class="bug-link" target="_blank" href="${bug_url}">BUG-${response.bug_id}</a>`);
                } else {
                    $(result_cell_id).addClass('bg-' + result_status);
                    $(result_cell_id).text(result_status_text);
                }
                $('#update-result-modal').modal('toggle');
            },
            error: function(error){
                alert("Unable to update result. Please see system administrator.");
                console.log("Something went wrong", error);
            }
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

    $(function() {
        $.contextMenu({
            selector: '.dashboard-date-cell', 
            callback: function(key, options) {
                if (key == 'delete-results') {
                    var date = $(this).data('date')
                    var suite = $('#dashboard-table').data('suite-name');
                    if (confirm('Are you sure you want to delete these results?') == true) {
                        $.ajax({
                            url: '/api/delete/test-results/' + suite + '/' + date,
                            type: "POST",
                            headers:{
                                "X-CSRFToken": csrftoken,
                            },
                            cache: false,
                            contentType: false,
                            processData: false,
                            success: function (response) {
                                alert('Succesfully deleted results for ' + suite + '(' + date + ')');
                            },
                            error: function(error){
                                alert('An error occured while trying to delete results...');
                                console.log("Something went wrong", error);
                            }
                        });
                    }
                }
                location.reload();
            },
            items: {
                "delete-results": {name: "Delete Results", icon: "delete"},
            }
        });
    });

});