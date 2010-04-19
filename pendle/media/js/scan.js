jQuery(function($) {
    var Drawer = {
        _init: function() {
            this.options.button = $(this.options.button);
            this.options.button.bind('click.drawer', {drawer: this}, function(e) {
                e.data.drawer.toggle();
                e.data.drawer._trigger('click');
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
        load: function(url, data) {
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
                    this.options.content = $(response).hide().appendTo(this.element).slideDown('fast');
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
            this.options.input.blur(function(e) {
                var query = $(this).val();
                scanner.scan(query, false);
            });
            this.options.browser.drawer({
                button: this.options.button,
                click: function() {
                    scanner.focus();
                },
                open: function() {
                    var browser = $(this);
                    browser.drawer('option', 'button').addClass('open');
                    scanner.browse();
                },
                close: function(focus) {
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
                var value = $(this).closest('tr').find('td:first').text();
                scanner.reset(false);
                scanner.options.input.val(value);
                scanner.options.browser.drawer('close');
                scanner.options.form.submit();
            });
            $('a.all', this.options.browser).live('click', function(e) {
                scanner.reset(true).focus();
                scanner.options.form.submit();
            });
            $('ul.filter a, a.filter', this.options.browser).live('click', function(e) {
                var url = $(this).attr('href');
                scanner.options.browser.drawer('load', url);
                return false;
            });
        },
        scan: function(query, force) {
            query = $.trim(query);
            this._trigger('scan', null, {query: query, force: force});
            if (force || (query && query != this.options.query)) {
                this.options.query = query;
                this.send(query);
            }
            return this;
        },
        send: function(query) {
            this.focus();
            if (!this.options.browser.drawer('option', 'isOpen')) {
                this.reset(false, !query);
                if (query) {
                    $.ajax({
                        beforeSend: function(request) {
                            if (this.options.request) {
                                this.options.request.abort();
                            }
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
            }
            else {
                this.browse();
            }
            this._trigger('send', null, {query: query});
            return this;
        },
        receive: function(response) {
            this._trigger('receive', null, {response: response});
            if (this.options.content) {
                this.options.content.remove();
            }
            if (response.html) {
                this.options.content = $(response.html).hide().appendTo(this.element);
                if (!this.options.browser.drawer('option', 'isOpen')) {
                    this.options.content.slideDown('fast');
                }
                this._trigger('ready', null, {response: response});
            }
            return this;
        },
        reset: function(clear, animate) {
            animate = (typeof animate == 'undefined') ? true : animate;
            if (clear) {
                this.options.input.val("");
            }
            if (this.options.content) {
                var speed = animate ? 'fast' : 0;
                this.options.content.slideUp(speed, function(e) {
                    $(this).remove();
                });
            }
            return this;
        },
        focus: function() {
            this.options.input.focus().select();
            return this;
        },
        browse: function() {
            var browser = this.options.browser;
            var form = this.options.form;
            var query = this.options.query;
            if (this.options.content) {
                this.options.content.slideUp('fast');
            }
            if (!browser.drawer('option', 'content') || browser.data('query') != query) {
                browser.data('query', query);
                var url = form.attr('action') + '/browse';
                var data = form.serializeArray();
                browser.drawer('load', url, data);
            }
            this._trigger('browse');
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
        name: 'customer',
        ready: function() {
            $('#scan-asset').scanner('focus');
        },
        browse: function() {
            $('#scan-asset').scanner('option', 'browser').drawer('close', false);
        }
    }).scanner('focus');
    $('#scan-asset').scanner({
        name: 'asset',
        browse: function() {
            $('#scan-customer').scanner('option', 'browser').drawer('close', false);
        }
    });
});
