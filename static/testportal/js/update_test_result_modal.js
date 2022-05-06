$(document).ready(function() {
    $('#test-result-status').on('change', function () {
        var selected_status = $('#test-result-status option:selected').text();
        var note_field = $('#test-result-note');
        var today = new Date().toLocaleDateString();
        var user = $('#test-result-user option:selected').text();

        switch (selected_status) {
            case 'Pass':
                note_field.val(`Test passed.`);
                break;
            case 'Fail':
                note_field.val('Test failed.');
                break;
            case 'False Negative':
                note_field.val(`Date: ${today}\nReason: \nAction: `);
                break;
            case 'Issue':
                note_field.val(`Reporter: ${user}\nDate: ${today}\nSummary: `);
                break;
            case 'Skipped':
                note_field.val(`Reason: `);
                break;
            case 'Under Construction':
                note_field.val(`Construction Start Date: ${today}\nProblem: `);
                break;
            case 'In Documentation':
                note_field.val(`Documentation Report Date: ${today}\nReported to: \nReported By: ${user}\nProblem: `);
                break;
        }
    });
});