$(document).ready(function () {
    $('#collapse_category').on('click', '.fa-chevron-right,.fa-chevron-down',function() {
         $(this).parent().find('ul:first').toggle('normal');
         $(this).toggleClass('fa-chevron-down fa-chevron-right');
    });
});
