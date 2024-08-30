$(document).ready(function() {
    $('#deleteConfirmButton').click(function() {
        var taskid = $(this).data('task-id');
        $.ajax({
            url: '/delete_task/' + rowid,
            type: 'POST',
            success: function(response) {
                $('#confirmDeleteModal').modal('hide');

                document.querySelector('#confirmDeleteModal button[data-bs-dismiss="modal"]').click();
                // Refresh the table or remove the row from the table
                // $('tr#' + rowid).remove();
                location.reload();
            },
            error: function(xhr, status, error) {
                // Handle error
                console.error("Error: " + error);
            }
        });
    });
});