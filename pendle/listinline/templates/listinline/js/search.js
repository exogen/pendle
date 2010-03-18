{% with inline_admin_formset.opts.opts as opts %}
jQuery(function($) {
    $('.list-inline .search input[name=query]').change(function(e) {
        var query = $(this).val();
        var search_url = '{% url listinline:search opts.app_label opts.module_name %}';
        alert(search_url);
    });
});
{% endwith %}
