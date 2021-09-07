$(document).ready(function () {
    function resetForm($form) {
      $form.find('input:text, input:hidden').val('');
      $form.find('.break_danger').css('display', 'block');
      $form.find('.break_danger').val('-');
    }

    function addDP($els) {
      $els.datetimepicker({
        format: 'LT'
      });
    }

    $('.break_success').on('click', function () {
      var btn_name = $(this).attr('name');
      var split_name = btn_name.split("_");

      var $blankClone = $("." + split_name[0] + "_" + split_name[1] + "_append_break:first").clone();
      resetForm($blankClone);
      $blankClone.appendTo("." + split_name[0] + "_" + split_name[1] + "_break");

      addDP($('input.datetimepicker'));
    });
});
