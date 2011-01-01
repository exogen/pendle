jQuery(function($) {
    var pendle = window.__pendle__ || {};

    $('#activity-options').drawer({
        button: '#activity-options-toggle',
        open: function() {
            var drawer = $(this);
            if (drawer.drawer('option', 'content') === null) {
                drawer.drawer('load', pendle.activity_options_url);
            }
        }
    });
    $('#activity-options form').live('submit', function(e) {
        var form = $(this);
        $.ajax({
            cache: false,
            context: this,
            data: form.serializeArray(),
            success: function(response, status) {
                $('#activity-options').drawer('option', 'content').replaceWith(response);
                $('#activity-options').drawer('close');
            },
            timeout: 15000,
            type: form.attr('method'),
            url: form.attr('action')
        });
        return false;
    });
    $('#activity-options-cancel').live('click', function(e) {
        var drawer = $('#activity-options').drawer('close');
        $('form', drawer).get(0).reset();
    });
});

