$(function() {
    // show/hide filter panel
    setTimeout('$("#sidebar").toggleClass("collapsed");\
        $("#content").toggleClass("col-md-12 col-md-10")', 1000);
    $('.toggle-sidebar').click(function() {
        $('#sidebar').toggleClass('collapsed');
        $('#content').toggleClass('col-md-12 col-md-10');
        return false;
    });
    // pagination
    $('#row-main').on('click', '.pagination a[href*="page"]', function(event) {
        event.preventDefault();
        $('#table').load($(this).prop('href') + ' #table');
        $('html, body').animate({scrollTop: 0}, 500);
    });
    // column sorting
    $('#row-main').on('click', '.orderable a', function(event) {
        event.preventDefault();
        $('#table').load($(this).prop('href') + ' #table')
    });
    // filtering
    $('#filter').on('click', 'input[name="filter"]', function(event) {
        event.preventDefault();
        apply_filter();
    });
});

function apply_filter() {
    var data = {};
    $('[class*="form-control"]').each(function(i, el) {
        var name = $(el).prop('name');
        data[name] = $(el).val();
    });
    console.log(data);
    $.ajax({
        url: window.location.href,
        type: 'get',
        data: data,
        success: function(data) {
            $('#content').html($('#content', data).html());
        },
        error: function(xhr, errmsg, err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
}
