$(document).ready(function(){
    $('.sidenav').sidenav({edge: "right"});
    $(".dropdown-trigger").dropdown();
    $('.collapsible').collapsible();
    $('select').formSelect();
    $('.datepicker').datepicker({
        format: "yyyy/mm/dd",
        yearRange:3,
        showClearBtn: true,
        i18n: {
            done: "select"
        }
    });
  });
