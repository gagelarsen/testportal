
$(document).ready(function() {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    function toDateInputValue(value) {
        if (!value) {
            return '';
        }
        return value.toString().slice(0, 10);
    }

    function todaysDateString() {
        const now = new Date();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        return `${now.getFullYear()}-${month}-${day}`;
    }

    function resetBugVerificationModalForCreate() {
        $('#bug-verification-modal-title').text('Add Bug Verification');
        $('#bug-verification-modal-save').text('Create');
        $('#bug-verification-id').val('');
        $('#bug-verification-bug-id').val('');
        $('#bug-verification-summary').val('');
        $('#bug-verification-test').val('nongui');
        const today = todaysDateString();
        $('#bug-verification-reported').val(today);
        $('#bug-verification-fixed').val(today);
        $('#bug-verification-verified').val(today);
        $('#bug-verification-category').prop('selectedIndex', 0);
        $('#bug-verification-products').val([]);
        $('#bug-verification-modal-error').hide().text('');
    }

    function populateBugVerificationModal(response) {
        $('#bug-verification-modal-title').text('Edit Bug Verification');
        $('#bug-verification-modal-save').text('Update');
        $('#bug-verification-id').val(response.id);
        $('#bug-verification-bug-id').val(response.bug_id || '');
        $('#bug-verification-summary').val(response.summary || '');
        $('#bug-verification-test').val(response.test || 'nongui');
        $('#bug-verification-reported').val(toDateInputValue(response.reported_date));
        $('#bug-verification-fixed').val(toDateInputValue(response.fixed_date));
        $('#bug-verification-verified').val(toDateInputValue(response.verified_date));

        const categoryId = response.category && typeof response.category === 'object'
            ? response.category.id
            : response.category;
        $('#bug-verification-category').val(String(categoryId));

        const productIds = (response.products || []).map(function(item) {
            if (typeof item === 'object') {
                return String(item.id);
            }
            return String(item);
        });
        $('#bug-verification-products').val(productIds);
        $('#bug-verification-modal-error').hide().text('');
    }

    function showBugVerificationError(message) {
        $('#bug-verification-modal-error').text(message).show();
    }

    window.openBugVerificationModal = function(verificationId) {
        $('#bug-verification-modal-error').hide().text('');

        if (!verificationId) {
            resetBugVerificationModalForCreate();
            $('#bug-verification-modal').modal('show');
            return;
        }

        $('#bug-verification-modal-title').text('Edit Bug Verification');
        $('#bug-verification-modal-save').text('Update');
        $('#bug-verification-modal').modal('show');

        $.ajax({
            url: '/api/bug-verifications/' + verificationId + '/',
            type: 'GET',
            headers: { 'X-CSRFToken': csrftoken },
            dataType: 'json',
            success: function(response) {
                populateBugVerificationModal(response);
            },
            error: function() {
                showBugVerificationError('Unable to load bug verification details.');
            }
        });
    };

    $('#bug-verification-modal-save').on('click', function() {
        const verificationId = $('#bug-verification-id').val();
        const payload = {
            bug_id: Number($('#bug-verification-bug-id').val()),
            summary: $('#bug-verification-summary').val(),
            products: ($('#bug-verification-products').val() || []).map(Number),
            reported_date: $('#bug-verification-reported').val(),
            fixed_date: $('#bug-verification-fixed').val(),
            verified_date: $('#bug-verification-verified').val(),
            category: Number($('#bug-verification-category').val()),
            test: $('#bug-verification-test').val(),
        };

        if (!payload.bug_id || !payload.summary || !payload.reported_date || !payload.fixed_date || !payload.verified_date || !payload.category) {
            showBugVerificationError('Please fill in bug id, summary, dates, and category.');
            return;
        }

        const isUpdate = Boolean(verificationId);
        const url = isUpdate ? '/api/bug-verifications/' + verificationId + '/' : '/api/bug-verifications/';
        const method = isUpdate ? 'PUT' : 'POST';

        $.ajax({
            url: url,
            type: method,
            data: JSON.stringify(payload),
            contentType: 'application/json',
            processData: false,
            headers: { 'X-CSRFToken': csrftoken },
            dataType: 'json',
            success: function() {
                $('#bug-verification-modal').modal('hide');
                location.reload();
            },
            error: function(error) {
                let message = 'Unable to save bug verification.';
                if (error.responseJSON) {
                    message = JSON.stringify(error.responseJSON);
                }
                showBugVerificationError(message);
            }
        });
    });

    $(function() {
        $.contextMenu({
            selector: '.verification-row', 
            callback: function(key, options) {
                var verification_id = $(this).data('verification-id');
                if (key == 'edit-verification') {
                    window.openBugVerificationModal(verification_id);
                }
            },
            items: {
                "edit-verification": {name: "Edit Verification", icon: "fa-thin fa-pen-to-square"},
            }
        });
    });
});