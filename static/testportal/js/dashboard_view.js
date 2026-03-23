
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
    
    // Open Modal for Result
    $(document).on('dblclick', '.test-result-dashboard-cell', function() {
        var result_id = this.dataset.resultId;

        if (result_id == undefined) {
            return;
        }
        
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
                var current_user = $('#dashboard-table').data('current-user-id');

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

        var url = `/api/test-results/${result_id}/`;
        var method = 'PUT';
        var is_create_result = false;

        if (result_id == '') {
            url = `/api/test-results/`;
            method = 'POST';
            is_create_result = true;
        }

        $.ajax({
            url: url,
            type: method,
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
                var form_result_id = $('#test-result-id').val();
                var result_status = $('#test-result-status').val();
                var result_status_text = $('#test-result-status option:selected').text().trim();
                var display_user = $('#test-result-user option:selected').text().trim();
                var normalized_result_id = (form_result_id == '' || form_result_id == 'undefined') ? String(response.id) : String(form_result_id);
                var test_case_id = $('#test-result-test-case').val();
                var result_date = $('#test-result-date').val();

                $('#update-result-modal').modal('toggle');

                ensure_result_cell_exists(
                    normalized_result_id,
                    test_case_id,
                    result_date
                );

                update_result_cell(
                    normalized_result_id,
                    result_status,
                    result_status_text,
                    response.note,
                    response.bug_id,
                    display_user,
                );

                if (is_create_result) {
                    show_dashboard_toast('Result Created', 'New result saved successfully.');
                } else {
                    show_dashboard_toast('Result Updated', 'Changes saved successfully.');
                }
            },
            error: function(error){
                show_dashboard_toast('Save Failed', 'Unable to update result. Please try again.');
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

    // Date Context Menu
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
                    location.reload();
                }
            },
            items: {
                "delete-results": {name: "Delete Results", icon: "delete"},
            }
        });
    });

    // Test Case Context Menu
    $(function() {
        $.contextMenu({
            selector: '.test-case-name-dashboard-cell', 
            callback: function(key, options) {
                var case_id = $(this).data('test-case-id');
                if (key == 'delete-test-case') {
                    var case_name = $(this).text().trim();
                    var table_row = $(this).closest('tr');
                    if (confirm(`Are you sure you want to delete this test case? (${case_name})`) == true) {
                        $.ajax({
                            url: `/api/delete/test-cases/${case_id}`,
                            type: "POST",
                            headers:{
                                "X-CSRFToken": csrftoken,
                            },
                            cache: false,
                            contentType: false,
                            processData: false,
                            success: function (response) {
                                alert(`Succesfully deleted test case - ${case_name}`);
                                table_row.remove();
                            },
                            error: function(error){
                                alert('An error occured while trying to delete results...');
                                console.log("Something went wrong", error);
                            }
                        });
                    }
                } else if (key == 'view-test-case') {
                    window.location = `/test-cases/${case_id}`;
                } else if (key == 'edit-test-case') {
                    if (typeof window.openTestCaseModal === 'function') {
                        window.openTestCaseModal(case_id);
                    } else {
                        window.location = `/test-cases/${case_id}/update`;
                    }
                }
            },
            items: {
                "delete-test-case": {name: "Delete Test Case", icon: "fa-thin fa-trash"},
                "view-test-case": {name: "View Test Case", icon: "fa-thin fa-eye"},
                "edit-test-case": {name: "Edit Test Case", icon: "fa-thin fa-pen-to-square"},
            }
        });
    });

    // Test Result Context Menu
    $(function() {
        $.contextMenu({
            selector: '.test-result-dashboard-cell',
            build: function($trigger, e) {
                var isFailCell = $trigger.hasClass('bg-fail');
                var menuItems = {
                    "copy-result-to-current": {name: "Copy Result to Current", icon: "copy"},
                };
                if (isFailCell) {
                    menuItems["passed-on-rerun"] = {name: "Passed on Rerun", icon: "edit"};
                }

                return {
                    callback: function(key, options) {
                        if (key == 'copy-result-to-current') {
                            var result_id = $(this).data('result-id');
                            var table_row = $(this).closest('tr');
                            var test_case_name = table_row.data('test-case-name');
                            if (confirm(`Are you sure you want to this result to the most recent result? (${test_case_name})`) == true) {
                                $.ajax({
                                    url: `/api/copy-result-to-latest/${result_id}`,
                                    type: "POST",
                                    headers:{
                                        "X-CSRFToken": csrftoken,
                                    },
                                    cache: false,
                                    contentType: false,
                                    processData: false,
                                    success: function (response) {
                                        update_result_cell(
                                            String(response.updated_result_id),
                                            response.updated_result_status,
                                            response.updated_result_status_text,
                                            response.updated_result_note,
                                            response.updated_result_bug_id,
                                            response.updated_result_user,
                                        );
                                    },
                                    error: function(error){
                                        alert(error.statusText);
                                        console.log("Something went wrong", error);
                                    }
                                });
                            }
                        } else if (key == 'passed-on-rerun') {
                            var rerun_result_id = $(this).data('result-id');
                            var rerun_date = $(this).data('result-date');
                            var active_user_id = $('#dashboard-table').data('current-user-id');
                            var active_user_name = $('#dashboard-table').data('current-user-name');
                            var rerun_note = `Date: ${rerun_date}\nReason: Failed on nightly run\nAction: Passed when run manually`;

                            $.ajax({
                                url: `/api/test-results/${rerun_result_id}/`,
                                type: "PATCH",
                                data: {
                                    'user': active_user_id,
                                    'result': 'false-negative',
                                    'note': rerun_note,
                                    'bug_id': '',
                                },
                                headers:{
                                    "X-CSRFToken": csrftoken,
                                },
                                dataType:'json',
                                success: function (response) {
                                    update_result_cell(
                                        String(rerun_result_id),
                                        'false-negative',
                                        'False Negative',
                                        response.note,
                                        response.bug_id,
                                        active_user_name,
                                    );
                                    show_dashboard_toast('Marked as Passed on Rerun', 'Result updated to False Negative.');
                                },
                                error: function(error){
                                    alert('Unable to mark as passed on rerun.');
                                    console.log("Something went wrong", error);
                                }
                            });
                        }
                    },
                    items: menuItems
                };
            }
        });
    });
    
    $(document).on('dblclick', '.no-result-dashboard-cell', function() {
        $('#update-result-modal-loading').show();
        $('#update-result-modal-form').hide();
        $('#update-result-modal-error').hide();

        var test_case_name = $(this).parent().data('test-case-name');
        var test_case_id = $(this).parent().data('test-case-id');
        var today = $(this).data('result-date');
        var current_user = $('#dashboard-table').data('current-user-id');
        
        $('#update-result-modal').modal('toggle');
        $('#update-result-modal-lable').text('Update Result for ' + test_case_name);
        $('#update-result-modal-accept').data('test-result-id', undefined);

        $('#test-result-id').val(undefined);
        $('#test-result-test-case').val(test_case_id);
        $('#test-result-date').val(today);
        $('#test-result-status').val('skipped');
        $('#test-result-user').val(current_user);
        $('#test-result-note').val('');
        $('#test-result-duration').val(0.0);
        $('#test-result-duration').attr('disabled', false);
        $('#test-result-bug-id').val('');
                
        $('#update-result-modal-loading').hide();
        $('#update-result-modal-form').show();
        $('#update-result-modal-error').hide();
    });

});

function ensure_result_cell_exists(result_id, test_case_id, result_date) {
    var result_cell_id = '#result-cell-id-' + result_id;
    if ($(result_cell_id).length > 0) {
        return;
    }

    var row_selector = `#dashboard-table tr.test-case-row[data-test-case-id="${test_case_id}"]`;
    var no_result_cell_selector = `td.no-result-dashboard-cell[data-result-date="${result_date}"]`;
    var no_result_cell = $(row_selector).find(no_result_cell_selector).first();

    if (no_result_cell.length === 0) {
        return;
    }

    no_result_cell
        .attr('id', 'result-cell-id-' + result_id)
        .attr('data-result-id', result_id)
        .removeClass('no-result-dashboard-cell')
        .addClass('test-result-dashboard-cell');
}

function show_dashboard_toast(title, message) {
    var container = document.getElementById('dashboard-toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'dashboard-toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1080';
        document.body.appendChild(container);
    }

    var toast = document.createElement('div');
    toast.className = 'toast border-0';
    toast.role = 'status';
    toast.ariaLive = 'polite';
    toast.ariaAtomic = 'true';
    toast.innerHTML = `
        <div class="toast-header">
            <strong class="me-auto">${title}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">${message}</div>
    `;

    container.appendChild(toast);
    var toastInstance = bootstrap.Toast.getOrCreateInstance(toast, { delay: 2200 });
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
    toastInstance.show();
}

function update_result_cell(result_id, result_status, result_status_text,
                            result_note, result_bug_id, result_user) {
    // Update table
    var result_cell_id = '#result-cell-id-' + result_id;
    var result_cell = $(result_cell_id);

    if (result_cell.length === 0) {
        return;
    }

    $("#test-result-status option").map(function() {
        $(result_cell_id).removeClass('bg-' + this.value);
    });
    $(result_cell_id).removeClass('bg-bug');

    var tooltip_instance = bootstrap.Tooltip.getInstance(result_cell[0]);
    if (tooltip_instance) {
        tooltip_instance.dispose();
    }

    $(result_cell_id).html('');
    $(result_cell_id)
        .attr('data-bs-toggle', 'tooltip')
        .attr('data-bs-placement', 'bottom')
        .attr('data-bs-html', 'true')
        .attr('data-bs-title', `${result_user}<br>${result_note || ''}`);
    
    var normalized_bug_id = result_bug_id || '';

    if (normalized_bug_id !== '') {
        $(result_cell_id).addClass('bg-bug');
        var bug_url = `https://bugs.aquaveo.com/view.php?id=${normalized_bug_id}`;
        $(result_cell_id).html(`<a class="bug-link" target="_blank" href="${bug_url}">BUG-${normalized_bug_id}</a>`);
    } else {
        $(result_cell_id).addClass('bg-' + result_status);
        $(result_cell_id).text(result_status_text);
    }

    bootstrap.Tooltip.getOrCreateInstance(result_cell[0], { delay: { show: 150, hide: 75 } });
}