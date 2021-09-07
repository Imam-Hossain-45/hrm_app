$(document).ready(function () {
  function addDP($els) {
      $els.datetimepicker({
          format: 'LT'
      });
  }

  $("[name='parent_schedule']").on('change', function () {
      $.ajax({
          url: ".",
          data: {'parent_id': $(this).val()},
          success: function (result) {
              $(".parent_form").html(result);
              $("input[name='fixedForm-INITIAL_FORMS']").val(0);
              var i = 0;
              for (i = 0; i < 7; i++) {
                $("input[name="+"'"+i+"-INITIAL_FORMS']").val(0);
              }
              scheduleType();
              rosterType();
              addDP($('input.datetimepicker'));
          }
      });
  });
  scheduleType();
  rosterType();
});

function attrChangeName(elem, attr, new_attr) {
  var data = $(elem).attr(attr);
  $(elem).attr(new_attr, data);
  $(elem).removeAttr(attr);
}

function scheduleType() {
  var schedule = document.getElementById('id_schedule_type').value;
  if (schedule == 'regular-fixed-time') {

    $('.regular-fixed-time').css('display', 'block');
    $('.regular-fixed-time').find('*').each(function () {
      if ($(this).attr('data')) {
        attrChangeName($(this), 'data', 'name');
      }

    });

    $('.fixed-day, .day, .hourly, .weekly, .freelancing, .roster-fixed, .roster-variable, .flexible, .roster_type').css('display', 'none');
    $('.fixed-day, .day, .hourly, .weekly, .freelancing, .roster-fixed, .roster-variable, .flexible, .roster_type').find('*').each(function () {
      if ($(this).attr('name')) {
        attrChangeName($(this), 'name', 'data');
      }

    });

  }
  else if (schedule == 'fixed-day') {

    $('.fixed-day').css('display', 'block');
    $('.fixed-day').find('*').each(function () {
      if ($(this).attr('data')) {
        attrChangeName($(this), 'data', 'name');
      }

    });

    $('.regular-fixed-time, .day, .hourly, .weekly, .freelancing, .roster-fixed, .roster-variable, .flexible, .roster_type').css('display', 'none');
    $('.regular-fixed-time, .day, .hourly, .weekly, .freelancing, .roster-fixed, .roster-variable, .flexible, .roster_type').find('*').each(function () {
      if ($(this).attr('name')) {
        attrChangeName($(this), 'name', 'data');
      }

    });

  }
  else if (schedule == 'hourly') {

    $('.fixed-day, .day, .regular-fixed-time, .weekly, .freelancing, .roster-fixed, .roster-variable, .flexible, .roster_type').css('display', 'none');
    $('.fixed-day, .day, .regular-fixed-time, .weekly, .freelancing, .roster-fixed, .roster-variable, .flexible, .roster_type').find('*').each(function () {
      if ($(this).attr('name')) {
        attrChangeName($(this), 'name', 'data');
      }

    });

    $('.hourly').css('display', 'block');
    $('.hourly').find('*').each(function () {
      if ($(this).attr('data')) {
        attrChangeName($(this), 'data', 'name');
      }

    });
  }
  else if (schedule == 'weekly') {

    $('.fixed-day, .day, .regular-fixed-time, .hourly, .freelancing, .roster-fixed, .roster-variable, .flexible, .roster_type').css('display', 'none');
    $('.fixed-day, .day, .regular-fixed-time, .hourly, .freelancing, .roster-fixed, .roster-variable, .flexible, .roster_type').find('*').each(function () {
      if ($(this).attr('name')) {
        attrChangeName($(this), 'name', 'data');
      }

    });

    $('.weekly').css('display', 'block');
    $('.weekly').find('*').each(function () {
      if ($(this).attr('data')) {
        attrChangeName($(this), 'data', 'name');
      }

    });

  }
  else if (schedule == 'day') {

    $('.fixed-day, .weekly, .regular-fixed-time, .hourly, .freelancing, .roster-fixed, .roster-variable, .flexible, .roster_type').css('display', 'none');
    $('.fixed-day, .weekly, .regular-fixed-time, .hourly, .freelancing, .roster-fixed, .roster-variable, .flexible, .roster_type').find('*').each(function () {
      if ($(this).attr('name')) {
        attrChangeName($(this), 'name', 'data');
      }

    });

    $('.day').css('display', 'block');
    $('.day').find('*').each(function () {
      if ($(this).attr('data')) {
        attrChangeName($(this), 'data', 'name');
      }

    });

  }
  else if (schedule == 'freelancing') {

    $('.fixed-day, .weekly, .regular-fixed-time, .hourly, .day, .roster-fixed, .roster-variable, .flexible, .roster_type').css('display', 'none');
    $('.fixed-day, .weekly, .regular-fixed-time, .hourly, .day, .roster-fixed, .roster-variable, .flexible, .roster_type').find('*').each(function () {
      if ($(this).attr('name')) {
        attrChangeName($(this), 'name', 'data');
      }

    });

    $('.freelancing').css('display', 'block');
    $('.freelancing').find('*').each(function () {
      if ($(this).attr('data')) {
        attrChangeName($(this), 'data', 'name');
      }

    });

  }
  else if (schedule == 'roster') {

    $('.fixed-day, .weekly, .regular-fixed-time, .hourly, .day, .roster-fixed, .roster-variable, .flexible, .freelancing').css('display', 'none');
    $('.fixed-day, .weekly, .regular-fixed-time, .hourly, .day, .roster-fixed, .roster-variable, .flexible, .freelancing').find('*').each(function () {
      if ($(this).attr('name')) {
        attrChangeName($(this), 'name', 'data');
      }

    });

    $('.roster_type').css('display', 'block');
    $('.roster_type').find('*').each(function () {
      if ($(this).attr('data')) {
        attrChangeName($(this), 'data', 'name');
      }

    });


  }
  else if (schedule == 'flexible') {

    $('.fixed-day, .weekly, .regular-fixed-time, .hourly, .day, .roster-fixed, .roster-variable, .roster_type, .freelancing').css('display', 'none');
    $('.fixed-day, .weekly, .regular-fixed-time, .hourly, .day, .roster-fixed, .roster-variable, .roster_type, .freelancing').find('*').each(function () {
      if ($(this).attr('name')) {
        attrChangeName($(this), 'name', 'data');
      }

    });

    $('.flexible').css('display', 'block');
    $('.flexible').find('*').each(function () {
      if ($(this).attr('data')) {
        attrChangeName($(this), 'data', 'name');
      }

    });
  }
}

function rosterType() {
  var roster = document.getElementById('id_roster_type').value;
  if (roster == 'fixed-roster') {

    $('.fixed-day, .weekly, .regular-fixed-time, .hourly, .day, .flexible, .roster-variable, .roster_type, .freelancing').css('display', 'none');
    $('.fixed-day, .weekly, .regular-fixed-time, .hourly, .day, .flexible, .roster-variable, .roster_type, .freelancing').find('*').each(function () {
      if ($(this).attr('name')) {
        attrChangeName($(this), 'name', 'data');
      }

    });

    $('.roster-fixed, .roster_type').css('display', 'block');
    $('.roster-fixed, .roster_type').find('*').each(function () {
      if ($(this).attr('data')) {
        attrChangeName($(this), 'data', 'name');
      }

    });

  } else if (roster == 'variable-roster') {

    $('.fixed-day, .weekly, .regular-fixed-time, .hourly, .day, .flexible, .roster-fixed, .roster_type, .freelancing').css('display', 'none');
    $('.fixed-day, .weekly, .regular-fixed-time, .hourly, .day, .flexible, .roster-fixed, .roster_type, .freelancing').find('*').each(function () {
      if ($(this).attr('name')) {
        attrChangeName($(this), 'name', 'data');
      }

    });

    $('.roster-variable, .roster_type').css('display', 'block');
    $('.roster-variable, .roster_type').find('*').each(function () {
      if ($(this).attr('data')) {
        attrChangeName($(this), 'data', 'name');
      }

    });
  }
}
