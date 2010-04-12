jQuery(function($) {
    var Drawer = {
        _init: function() {
            this.options.button = $(this.options.button);
            this.options.button.bind('click.drawer', {drawer: this}, function(e) {
                e.data.drawer.toggle();
            });
        },
        open: function() {
            this.options.isOpen = true;
            this._trigger('open');
            var drawer = this;
            this.element.slideDown('fast', function() {
                drawer._trigger('opened');
            });
        },
        close: function() {
            this.options.isOpen = false;
            this._trigger('close');
            var drawer = this;
            this.element.slideUp('fast', function() {
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
        options: {
            isOpen: false
        }
    };
    $.widget('ui.drawer', Drawer);
    var Scanner = {
        _init: function() {
            this.options.input = $(this.options.input, this.element);
            this.options.form = $(this.options.form, this.element);
            this.options.browser = $(this.options.browser, this.element);
            this.options.button = $(this.options.button, this.element);
            var scanner = this;
            this.options.form.submit(function(e) {
                var query = scanner.options.input.val();
                scanner.scan(query, true);
                return false;
            });
            this.options.input.change(function(e) {
                var query = $(this).val();
                scanner.scan(query, false);
            });
            this.options.browser.drawer({
                button: this.options.button,
                open: function() {
                    var browser = $(this);
                    scanner.options.input.focus().select();
                    scanner.reset(false);
                    browser.drawer('option', 'button').addClass('open');
                    var content = browser.data('content');
                    if (!content) {
                        browser.addClass('loading');
                        $.ajax({
                            beforeSend: function(request) {
                                this.data('request', request);
                            },
                            cache: false,
                            complete: function(response, status) {
                                this.removeClass('loading');
                            },
                            context: browser,
                            data: scanner.options.form.serializeArray(),
                            dataType: 'html',
                            success: function(response, status) {
                                var content = this.data('content');
                                if (content) {
                                    content.remove();
                                }
                                content = $(response).hide().appendTo(this).slideDown('fast');
                                this.data('content', content);
                            },
                            timeout: 15000,
                            type: 'GET',
                            url: scanner.options.form.attr('action') + '/browse'
                        });
                    }
                },
                close: function() {
                    scanner.options.input.focus().select();
                    if (scanner.options.content) {
                        scanner.options.content.slideDown('fast');
                    }
                },
                closed: function() {
                    var browser = $(this);
                    if (!browser.drawer('option', 'isOpen')) {
                        browser.drawer('option', 'button').removeClass('open');
                    }
                }
            });
            $('td', this.options.browser).live('click', function(e) {
                var value = $(this).closest('tr').find('td.username').text();
                scanner.options.input.val(value);
                scanner.options.browser.drawer('close');
                scanner.options.input.change();
            });
        },
        scan: function(query, force) {
            query = $.trim(query);
            this._trigger('scan', null, {query: query, force: force});
            if (force || query != this.options.query) {
                this.options.query = query;
                this.send(query);
            }
        },
        send: function(query) {
            if (this.options.request) {
                this.options.request.abort();
                this.reset(false);
            }
            if (query) {
                if (!this.options.browser.drawer('option', 'isOpen')) {
                    $.ajax({
                        beforeSend: function(request) {
                            this.options.request = request;
                        },
                        cache: false,
                        context: this,
                        data: this.options.form.serializeArray(),
                        dataType: 'json',
                        success: function(response, status) {
                            this.receive(response);
                        },
                        timeout: 15000,
                        type: this.options.form.attr('method'),
                        url: this.options.form.attr('action')
                    });
                }
                else {
                }
            }
            this._trigger('send', null, {query: query});
        },
        receive: function(response) {
            this._trigger('receive', null, {response: response});
            if (this.options.content) {
                this.options.content.remove();
            }
            if (response.html) {
                this.options.content = $(response.html).hide().appendTo(this.element).slideDown('fast');
                this._trigger('ready', null, {response: response});
            }
        },
        reset: function(clear) {
            if (clear) {
                this.options.input.val("");
            }
            if (this.options.content) {
                this.options.content.slideUp('fast');
            }
        },
        focus: function() {
            this.options.input.focus().select();
        },
        options: {
            input: 'input.query',
            form: 'form',
            browser: 'div.browse',
            button: 'button.browse'
        }
    };
    $.widget('ui.scanner', Scanner);

    $('#scan-customer').scanner({
        ready: function() {
            $('#scan-asset').scanner('focus');
        }
    }).scanner('option', 'input').focus();
    $('#scan-asset').scanner();
});
