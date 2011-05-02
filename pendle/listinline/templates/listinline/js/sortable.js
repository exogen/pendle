jQuery(function($) {
    $('#{{ group_id }}.inline-group').find('tbody').sortable({
        cancel: 'a, label, :input',
        containment: 'parent',
        cursor: 'move',
        items: 'tr',
        revert: 150,
        scrollSensitivity: 30,
        scrollSpeed: 10,
        tolerance: 'pointer',
        update: function(event, ui) {
            var group = $(this);
            group.find(group.sortable('option', 'items')).each(function(i) {
                var item = $(this);
                var is_new = !item.find(':input[name^={{ inline_admin_formset.formset.prefix }}-]' +
                                              '[name$=-{{ inline_admin_formset.opts.opts.pk.name }}]').val();
                if (!is_new) {
                    item.find('input[name$=-order]').val(i + 1);
                }
            });
        }
    }).addClass('sortable');
});
