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
    
    // Test Case Context Menu
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
                    window.location = `/test-cases/${case_id}/update`;
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