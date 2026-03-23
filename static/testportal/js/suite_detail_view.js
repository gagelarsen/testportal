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

    function setSelectedTagCheckboxes(tagIds) {
        var selected = new Set((tagIds || []).map(String));
        $('.test-case-tag-checkbox').each(function() {
            this.checked = selected.has(String(this.value));
        });
    }

    function getSelectedTagIds() {
        return $('.test-case-tag-checkbox:checked').map(function() {
            return Number(this.value);
        }).get();
    }

    function openTestCaseModal(caseId) {
        if ($('#update-test-case-modal').length === 0) {
            window.location = `/test-cases/${caseId}/update`;
            return;
        }

        $('#update-error').hide().text('');
        $('#update-test-case-modal-loading').show();
        $('#update-test-case-modal-form').hide();
        $('#update-test-case-modal').modal('show');

        $.ajax({
            url: '/api/test-cases/' + caseId + '/',
            type: 'GET',
            headers: { 'X-CSRFToken': csrftoken },
            dataType: 'json',
            success: function(response) {
                $('#test-case-id').val(response.id);
                $('#test-case-name').val(response.name || '');
                $('#test-case-test-id').val(response.test_case_id || '');
                $('#test-case-suite').val(response.suite);
                $('#test-case-status').val(response.status || 'active');
                $('#test-case-type').val(response.test_type || 'automated');
                setSelectedTagCheckboxes(response.tags || []);
                $('#test-case-categories').val(String(response.category));
                $('#test-case-subcategories').val(String(response.subcategory));
                $('#test-case-steps').val(response.steps || '');
                $('#view-test-case-button').attr('href', '/test-cases/' + response.id);

                $('#update-test-case-modal-loading').hide();
                $('#update-test-case-modal-form').show();
            },
            error: function() {
                $('#update-test-case-modal-loading').hide();
                $('#update-error').text('Unable to load test case details.').show();
            }
        });
    }

    window.openTestCaseModal = openTestCaseModal;

    $('#update-test-case-modal-accept').off('click.suiteDetail').on('click.suiteDetail', function() {
        var testCaseId = $('#test-case-id').val();
        if (!testCaseId) {
            $('#update-error').text('Missing test case id.').show();
            return;
        }

        var payload = {
            name: $('#test-case-name').val(),
            test_case_id: $('#test-case-test-id').val(),
            suite: Number($('#test-case-suite').val()),
            status: $('#test-case-status').val(),
            test_type: $('#test-case-type').val(),
            tags: getSelectedTagIds(),
            category: Number($('#test-case-categories').val()),
            subcategory: Number($('#test-case-subcategories').val()),
            steps: $('#test-case-steps').val(),
        };

        $.ajax({
            url: '/api/test-cases/' + testCaseId + '/',
            type: 'PUT',
            data: JSON.stringify(payload),
            contentType: 'application/json',
            processData: false,
            headers: { 'X-CSRFToken': csrftoken },
            dataType: 'json',
            success: function() {
                $('#update-test-case-modal').modal('hide');
                location.reload();
            },
            error: function(error) {
                var message = 'Unable to update test case.';
                if (error.responseJSON) {
                    message = JSON.stringify(error.responseJSON);
                }
                $('#update-error').text(message).show();
            }
        });
    });

     // Test Case Row Context Menu
     $(function() {
        $.contextMenu({
            selector: '.test-plan-test-case-row', 
            callback: function(key, options) {
                var case_id = $(this).data('test-case-id');
                if (key == 'delete-test-case') {
                    var case_name = $(this).data('test-case-name');
                    var table_row = $(this);
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
                    openTestCaseModal(case_id);
                }
            },
            items: {
                "delete-test-case": {name: "Delete Test Case", icon: "fa-thin fa-trash"},
                "view-test-case": {name: "View Test Case", icon: "fa-thin fa-eye"},
                "edit-test-case": {name: "Edit Test Case", icon: "fa-thin fa-pen-to-square"},
            }
        });
    });
});