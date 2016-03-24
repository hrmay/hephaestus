var accordion = function() {
    $('.accordion-content').slideUp('fast');
    $('#world-nav').find('.accordion-toggle').on('click', function() {
        window.console&&console.log('Clicked');
        if ($(this).next().is(':visible')) {
            window.console&&console.log('Sliding up other content');
            $(this).next().slideUp('fast');
        } else {
            window.console&&console.log('Sliding down other content');
            $(this).next().slideDown('fast');
        }
        $('.accordion-content').not($(this).next()).slideUp('fast');
    });
}

$(document).ready(function() {
    accordion();
});