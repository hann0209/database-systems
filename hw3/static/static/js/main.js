$(document).ready(function() {
    $('#login-form').on('submit', function(event) {
        event.preventDefault();
        const username = $('#username').val();
        const password = $('#password').val();

        $.post('/login', { username, password }, function(response) {
            if (response.success) {
                window.location.href = '/homepage';
            } else {
                $('#error-message').text(response.message);
            }
        });
    });

    $('#create-entry-form').on('submit', function(event) {
        event.preventDefault();
        const title = $('#title').val();
        const content = $('#content').val();

        $.post('/create', { title, content }, function(response) {
            if (response.success) {
                window.location.href = '/homepage';
            } else {
                alert('Failed to create entry');
            }
        });
    });
});
