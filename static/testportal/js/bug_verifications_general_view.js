
$(document).ready(function() {
    $(function() {
        $.contextMenu({
            selector: '.verification-row', 
            callback: function(key, options) {
                var verification_id = $(this).data('verification-id');
                if (key == 'edit-verification') {
                    window.open('/bug-verifications/' + verification_id + "/update", "_blank").focus();
                }
            },
            items: {
                "edit-verification": {name: "Edit Verification", icon: "fa-thin fa-pen-to-square"},
            }
        });
    });
});