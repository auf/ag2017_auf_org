(function( $ ){
    $.fn.act_sci_picker = function() {
        var picker_container = this;
        function ajaxify() {
            picker_container.find('a').click(function(e) {
                e.preventDefault();
                picker_container.load($(this).attr('href'), ajaxify);
            });
            picker_container.find('form').ajaxForm({
                target: picker_container,
                success: ajaxify
            });
        }
        picker_container.load('/activites_scientifiques/', ajaxify);
    };
})( jQuery );