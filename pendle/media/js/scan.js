jQuery(function($) {
    var CUSTOMER_FORM = $('#customer-form');
    var CUSTOMER_QUERY = $('#customer_query').focus();

    CUSTOMER_FORM.submit(function(e) {
        $(this).trigger('send', [true]);
        return false;
    }).bind('send', function(e, force) {
        var form = $(this);
        var query = $.trim(CUSTOMER_QUERY.val());
        if (force || query != form.data('query')) {
            form.data('query', query);
            if (query) {
                var data = {query: query};
                var request = $.ajax({
                    cache: false,
                    data: data,
                    dataType: 'json',
                    success: function(response, status) {
                        form.trigger('receive', [response]);
                    },
                    timeout: 15000,
                    type: 'GET',
                    url: form.attr('action')
                });
            }
        }
    }).bind('receive', function(e, response) {
        var form = $(this);
        if (response.html) {
            var html = $(response.html).appendTo(form);
        }
    });
});
