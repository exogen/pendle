jQuery(function($) {
    $('.list-inline').sortable({
        cancel: 'a, label, :input',
        containment: 'parent',
        cursor: 'move',
        items: 'li.inline-related',
        revert: 150,
        scrollSensitivity: 30,
        scrollSpeed: 10,
        tolerance: 'pointer',
        update: function(event, ui) {
            var group = $(this);
            var items = group.find(group.sortable('option', 'items'));
            items.each(function(i) {
                var item = $(this);
                var is_new = !item.find('input[name$=-id]').first().val();
                if (!is_new) {
                    item.find('input[name$=-bundle_order]').val(i + 1);
                }
            });
        }
    }).addClass('sortable');
});
