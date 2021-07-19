(function (define) {
    define(['jquery'], function ($) {
        return (function () {
            function open() {
                
            }

        })();
    });
}(typeof define === 'function' && define.amd ? define : function (deps, factory) {
    if (typeof module !== 'undefined' && module.exports) { //Node
        module.exports = factory(require('jquery'));
    }
    else if (window.layui && layui.define){
        layui.define('jquery', function (exports) { //layui加载
            exports('toastr', factory(layui.jquery));
            exports('notice', factory(layui.jquery));
        });
    }
    else {
        window.toastr = factory(window.jQuery);
    }
}));


        exports("rightmenu", {
        open: (args) => {
            var menu = createContainer();
            for (var row of args.items) {
                
            }
            
            return layer.open({
                
            }) 
        },

        createContainer: () {
            var ojb
            return $('<div class="rightmenu-container"></div>')
        }
    }