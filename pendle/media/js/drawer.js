jQuery(function($) {
    var Drawer = {
        _init: function() {
            this.options.button = $(this.options.button);
            this.options.button.bind('click.drawer', {drawer: this}, function(e) {
                e.data.drawer.toggle();
                e.data.drawer._trigger('click');
                return false;
            });
        },
        open: function(speed) {
            this.options.isOpen = true;
            this._trigger('open');
            var drawer = this;
            this.element.slideDown(speed || 'fast', function() {
                drawer._trigger('opened');
            });
        },
        close: function(speed) {
            this.options.isOpen = false;
            this._trigger('close');
            var drawer = this;
            this.element.slideUp(speed || 'fast', function() {
                drawer._trigger('closed');
            });
        },
        toggle: function() {
            if (this.options.isOpen) {
                this.close();
            }
            else {
                this.open();
            }
        },
        load: function(url, data, callback) {
            $.ajax({
                beforeSend: function(request) {
                    if (this.options.request) {
                        this.options.request.abort();
                    }
                    this.options.request = request;
                    if (this.options.content) {
                        this.options.content.remove();
                    }
                    this.element.addClass('loading');
                },
                cache: false,
                context: this,
                data: data,
                dataType: 'html',
                success: function(response, status) {
                    this.element.stop(true, true).removeClass('loading');
                    if (typeof callback == 'undefined') {
                        this.options.content = $(response).hide()
                            .appendTo(this.element).slideDown('fast');
                    }
                    else {
                        this.options.content = callback(response, status);
                    }
                },
                timeout: 15000,
                type: 'GET',
                url: url
            });
        },
        options: {
            content: null,
            isOpen: false
        }
    };
    $.widget('ui.drawer', Drawer);
});

