jQuery(document).ready(function ($) {

  // Product Filter
  var dropdowns = $(".dropdown");

  // Onclick on a dropdown, toggle visibility
  dropdowns.find("dt").click(function () {
    dropdowns.find("dd ul").hide();
    $(this).next().children().toggle();
  });

  // Clic handler for dropdown
  dropdowns.find("dd ul li a").click(function () {
    var leSpan = $(this).parents(".dropdown").find("dt a span");

    // Remove selected class
    $(this).parents(".dropdown").find('dd a').each(function () {
      $(this).removeClass('selected');
    });

    // Update selected value
    leSpan.html($(this).html());

    // If back to default, remove selected class else addclass on right element
    if ($(this).hasClass('default')) {
      leSpan.removeClass('selected');
    } else {
      leSpan.addClass('selected');
      $(this).addClass('selected');
    }

    // Close dropdown
    $(this).parents("ul").hide();
  });

  // Close all dropdown onclick on another element
  $(document).bind('click', function (e) {
    if (!$(e.target).parents().hasClass("dropdown")) {
      $(".dropdown dd ul").hide();
    }
  });

  // Prevent Toggle dropdown
  $('.cart-btn').click(function () {
    $('.cart-box').toggle();
  });

  $('a#profile').click(function () {
    $('.cart-box').css({
      "display": "none"
    });
  });

  $(".remove-row").parent().hide();


  $(".clone-row").on('click', function () {
    $(this).parent().parent().parent().find('.form-two').first().clone(true).appendTo($(this).parent().parent().siblings().closest(".form-one").find(".new-row"));

    var elm = $(this).parent().parent().siblings().closest(".new-row").find('.form-control');
    var len = elm.length;

    var lastElm = elm.last().find('input[type=text], select');
    var lastElmFirstInput = lastElm.first();
    var lastElmLastInput = lastElm.last();
    var lastElmLabel = elm.last().find('label');
    var lastElmFirstLabel = lastElmLabel.first();
    var lastElmLastLabel = lastElmLabel.last();
    var lastElmFirstInputId = lastElmFirstInput.attr('id');
    var lastElmLastInputId = lastElmLastInput.attr('id');
    var lastElmFirstInputName = lastElmFirstInput.attr('name');
    var lastElmLastInputName = lastElmLastInput.attr('name');
    // var firstId = lastElmFirstInputId.replace(/[0-9]/, len - 1);
    // var firstName = lastElmFirstInputName.replace(/[0-9]/, len - 1);
    // var lastId = lastElmLastInputId.replace(/[0-9]/, len - 1);
    // var lastName = lastElmLastInputName.replace(/[0-9]/, len - 1);

    // lastElmFirstInput.val('');
    // lastElmFirstInput.attr('id', firstId);
    // lastElmFirstInput.attr('name', firstName);
    // lastElmFirstLabel.attr('for', firstId);

    // lastElmLastInput.val('');
    // lastElmLastInput.attr('id', lastId);
    // lastElmLastInput.attr('name', lastName);
    // lastElmLastLabel.attr('for', lastId);

    $(this).parent().next().find(".remove-row").show();
    $(this).parent().next().find(".remove-row").parent().show();

    var regex = /[0-9]/;
    var newElm = $(this).parent().parent().parent().find('.new-row h2 span').last();
    var elmVal = newElm.text();

    newElm.html(elmVal.replace(regex, $(this).parent().parent().parent().find('.new-row h2 span').length + 1));

    // /[0-9]/

    // var hVal = parseInt(elmVal, 10) - 1); console.log(hVal); newElm.text(hVal);

    var newIndForm = $(this).parent().parent().parent().parent().find('#id_new_identification_form_prefix-TOTAL_FORMS');
    var newIndFormVal = newIndForm.val();

    newIndForm.val(parseInt(newIndFormVal, 10) + 1);
  });

  $(".remove-row").on('click', function () {
    // $(this).parent().parent().parent().find('.form-two').last().remove();

    if ($(this).parent().parent().parent().find('.form-two').length > 1) {
      $(this).parent().parent().parent().find('.form-two').last().find(".form-check-input").prop("checked", true);
      $(this).parent().parent().parent().find('.form-two').last().find(".m-checkbox").prop("checked", true);
      $(this).parent().parent().parent().find('.form-two').last().remove();
    }

    if ($(this).parent().parent().parent().find('.form-two').length === 1) {
      $(this).hide();
      $(this).parent().hide();
    }
    var newElm = $(this).parent().parent().parent().parent().find('.form-one input[name=fixedForm-TOTAL_FORMS]');
    var newElmVal = newElm.val();

    newElm.val(parseInt(newElmVal, 10) - 1);

    var newIndForm = $(this).parent().parent().parent().parent().find('#id_new_identification_form_prefix-TOTAL_FORMS');
    var newIndFormVal = newIndForm.val();

    newIndForm.val(parseInt(newIndFormVal, 10) - 1);

  });

  // New Identification Form value increment

  $('#department-form-submit').click(function (e) {
    var identificationForm = $('#department-form').find('.new-id-form').find(':input');

    $.each(identificationForm, function (i) {
      var attr = $(this).attr('type');
      var val = $(this).val();

      if (attr !== 'hidden' && attr !== 'checkbox' && val !== '') {
        $('#id_add_new').val(1);
      } else {
        $('#id_add_new').val(0);
      }
    });
  });


  // NEW
  function _playHideShow($this, elementId, value1, value2, option1, option2) {
    if ($this.val() === value1) {
      $(elementId + " ." + option1).show();
      $(elementId + " ." + option2).hide();
    }

    if ($this.val() === value2) {
      $(elementId + " ." + option2).show();
      $(elementId + " ." + option1).hide();
    }
  }

  function showSelectedEligibility(elementId, name, value1, value2, option1, option2) {
    $(elementId + " input[name=" + name + "]:checked").each(function (i) {
      _playHideShow($(this), elementId, value1, value2, option1, option2);
    });
  }

  function handleChangeEligibility(elementId, name, value1, value2, option1, option2) {
    $(elementId + " input[name=" + name + "]").each(function (i) {
      $(this).change(function () {
        _playHideShow($(this), elementId, value1, value2, option1, option2);
      });
    });
  }

  $('.nav-link').on('shown.bs.tab', function () {
    var id = $(this).attr('href');

    if ($(id).hasClass('active')) {
      var matches = id.match(/(\d+)/);

      if (matches) {
        var i = matches[0];

        showSelectedEligibility(id, i + "-eligibility_based_on", 'job_status_wise', 'time_wise', 'option-one', 'option-two');
        showSelectedEligibility(id, i + "-avail_based_on", 'job_status_wise', 'time_wise', 'option-three', 'option-four');
        handleChangeEligibility(id, i + "-eligibility_based_on", 'job_status_wise', 'time_wise', 'option-one', 'option-two');
        handleChangeEligibility(id, i + "-avail_based_on", 'job_status_wise', 'time_wise', 'option-three', 'option-four');
      }
    }
  });


  $(".clone-dt").on('click', function () {
    // $(this).parent().parent().find('.form-two').first().clone(true).appendTo($(this).parent().siblings().closest(".form-one").find(".new-row"));

    $('.datetimepicker').datetimepicker({
      showClear: true,
      useCurrent: false,
      format: 'LT'
    });


    var elm = $(this).parent().parent().parent().find('.form-two');
    var len = elm.length;
    var lastElm = elm.last().find('input[type=text]');
    var lastElmFirstInput = lastElm.first();
    var lastElmLastInput = lastElm.last();
    var lastElmLabel = elm.last().find('label');
    var lastElmFirstLabel = lastElmLabel.first();
    var lastElmLastLabel = lastElmLabel.last();
    var lastElmFirstInputId = lastElmFirstInput.attr('id');
    var lastElmLastInputId = lastElmLastInput.attr('id');
    var lastElmFirstInputName = lastElmFirstInput.attr('name');
    var lastElmLastInputName = lastElmLastInput.attr('name');
    var firstId = lastElmFirstInputId.replace(/[0-9]/, len - 1);
    var firstName = lastElmFirstInputName.replace(/[0-9]/, len - 1);
    var lastId = lastElmLastInputId.replace(/[0-9]/, len - 1);
    var lastName = lastElmLastInputName.replace(/[0-9]/, len - 1);

    lastElmFirstInput.val('');
    lastElmFirstInput.attr('id', firstId);
    lastElmFirstInput.attr('name', firstName);
    lastElmFirstLabel.attr('for', firstId);

    lastElmLastInput.val('');
    lastElmLastInput.attr('id', lastId);
    lastElmLastInput.attr('name', lastName);
    lastElmLastLabel.attr('for', lastId);

    $('#' + firstId).datetimepicker({
      showClear: true,
      sideBySide: true,
      useCurrent: false,
      format: 'LT'
    });
    $('#' + lastId).datetimepicker({
      showClear: true,
      sideBySide: true,
      useCurrent: false,
      format: 'LT'
    });

    var newElm = $(this).parent().parent().parent().parent().find('.form-one input[name=fixedForm-TOTAL_FORMS]');
    var newElmVal = newElm.val();

    newElm.val(parseInt(newElmVal, 10) + 1);

  });

  // Payroll master clone row
  $(".clone-pm").on('click', function () {
    var elm = $(this).parent().parent().parent().find('.new-row .form-two');
    var len = elm.length;

    $('.new-row .form-two').last().find(':input').each(function () {
      if ($(this).attr('id')) {
        var id = $(this).attr('id').replace(/[0-9]/g, len);
        $(this).attr('id', id);
      }
      var name = $(this).attr('name').replace(/[0-9]/g, len);

      $(this).attr('name', name);

      if ($(this).attr("type") == "hidden") {
        $(this).val("");
      }
    });

    $('.new-row .form-two').last().find('label').each(function () {
      var label = $(this).attr('for').replace(/[0-9]/g, len);
      $(this).attr('for', label);
    });

    var newElm = $(this).parent().parent().parent().parent().parent().find('.card-block input[name=rbr_set-TOTAL_FORMS]');
    var newElmVal = newElm.val();

    newElm.val(parseInt(newElmVal, 10) + 1);
  });

  $(".remove-row").on('click', function () {
    var newElm = $(this).parent().parent().parent().parent().parent().find('.card-block input[name=rbr_set-TOTAL_FORMS]');
    var newElmVal = newElm.val();

    newElm.val(parseInt(newElmVal, 10) - 1);
  });

  $(function () {
    $('.next-one').on('click', function () {
      $('.section-one').slideToggle();
    });
  });

  if ($('.next-one').prop('checked') == true) {
    $('.section-one').show();
  } else {
    $('.section-one').hide();
  }

  $(function () {
    $('.next-two').on('click', function () {
      $('.section-two').slideToggle();
    });
  });

  if ($('.next-two').prop('checked') == true) {
    $('.section-two').show();
  } else {
    $('.section-two').hide();
  }

  $(function () {
    $('.next-three').on('click', function () {
      $('.section-three').slideToggle();
    });
  });

  if ($('.next-three').prop('checked') == true) {
    $('.section-three').show();
  } else {
    $('.section-three').hide();
  }

  $(function () {
    $('.next-four').on('click', function () {
      $('.section-four').slideToggle();
    });
  });

  if ($('.next-four').prop('checked') == true) {
    $('.section-four').show();
  } else {
    $('.section-four').hide();
  }

  $(function () {
    $(".clone").on('click', function () {
      $(this).parent().siblings().closest(".form-two").each().clone(true).appendTo($(this).parent().siblings().closest(".row-field").after());
    });
  });

  $(function () {
    $(".remove").on('click', function () {
      $(this).parent().parent().find(".row-field").children(".form-two").remove();
    });
  });

  $(".remove-field").hide();

  $(".clone-field").on('click', function () {
    $(this).parent().parent().parent().find('.form-field').clone().attr('class', 'form-control mt-3').appendTo($(this).parent().parent().parent().find('.main'));

    var elm = $(this).parent().parent().parent().find('.form-control');
    var len = elm.length;

    var lastElm = elm.last();
    var lastId = lastElm.attr('id').replace(/[0-9]/, len - 1);
    var lastName = lastElm.attr('name').replace(/[0-9]/, len - 1);
    lastElm.val("");

    lastElm.attr('id', lastId);
    lastElm.attr('name', lastName);


    $(this).parent().parent().find(".remove-field").show();
  });

  $(".emergency-contact-add").on('click', function () {
    $(this).parent().parent().parent().find('tr.item').clone(true).appendTo($(this).parent().parent().parent().find('tbody.form-two').after());

    var elm = $(this).parent().parent().parent().find('tr');
    // var len = elm.length;

    // var lastElm = elm.last();
    // var lastId = lastElm.attr('id').replace(/[0-9]/, len - 1);
    // var lastName = lastElm.attr('name').replace(/[0-9]/, len - 1);
    // lastElm.val("");

    // lastElm.attr('id', lastId);
    // lastElm.attr('name', lastName);


    $(this).parent().parent().find(".remove-field").show();
  });

  $(".emergency-contact-rem").on('click', function () {
    var elm = $(this).parent().parent().parent().find('tr.item');

    if (elm.length > 1) {
      elm.last().remove();
    }

    if ($(this).parent().parent().parent().find('tr.item').length === 1) {
      $(this).hide();
    }
  });



  $(".remove-field").on('click', function () {
    var elm = $(this).parent().parent().parent().find('.form-control');

    if (elm.length > 1) {
      elm.last().remove();
    }

    if ($(this).parent().parent().parent().find('.form-control').length === 1) {
      $(this).hide();
    }
  });

  // Checkbox check toggle
  if ($(".check-one").prop('checked') == true) {
    $(".section-one").show();
  }

  if ($(".check-two").prop('checked') == true) {
    $(".section-two").show();
  }

  if ($(".check-three").prop('checked') == true) {
    $(".section-three").show();
  }

  // Employee Leave checkbox
  $(".overtime-check").change(function () {
    if (this.checked) {
      $(".overtime-wrap").show();
    } else {
      $(".overtime-wrap").hide();
    }
  });

  if ($(".overtime-check").prop('checked') == true) {
    $(".overtime-wrap").show();
  }

  $(".deduction-check").change(function () {
    if (this.checked) {
      $(".deduction-wrap").show();
    } else {
      $(".deduction-wrap").hide();
    }
  });

  if ($(".deduction-check").prop('checked') == true) {
    $(".deduction-wrap").show();
  }


  // User management Create User
  $('#id_user_type').change(function () {
    if ($(this).val() == 'employee-user') {
      $('.employee-select-box').show();
    } else {
      $('.employee-select-box').hide();
    }
  });

  // Employee master payment mode select
  // $('.emp-bank-info').hide();
  $('#id_payment_mode').change(function () {
    if ($(this).val() == 'bank') {
      $('.emp-bank-info').show();
    } else {
      $('.emp-bank-info').hide();
    }
  });

  // Employee master education
  $('#id_result_type').change(function () {
    if ($(this).val() == 'CGPA' || $(this).val() == 'GPA') {
      $('.result-gpa').show();
    } else {
      $('.result-gpa').hide();
    }
  });


  $('.result-division').hide();
  $('#id_result_type').change(function () {
    if ($(this).val() == 'division') {
      $('.result-division').show();
    } else {
      $('.result-division').hide();
    }
  });

  $('#id_same_as_present_address').change(function () {
    $('.permanent-address-wrap').slideToggle();
  });

  // Employee master DOB Field
  $('#id_date_of_birth').datetimepicker({
    icons: {
      time: "fa fa-clock-o",
      date: "fa fa-calendar",
      up: "fa fa-arrow-up",
      down: "fa fa-arrow-down"
    },
    maxDate: moment(),
    format: 'MM/DD/YYYY',
    useCurrent: false,
  });

  // Employee master Personal info
  $('#id_marital_status').change(function () {
    if ($(this).val() == 'married') {
      $('.spouce-info').show();
    } else {
      $('.spouce-info').hide();
    }
  });

  // User management workflow wrapper clone
  $('.workflow-option').change(function () {
    if ($(this).val() === 'and' || $(this).val() === 'or') {
      $(this).parent().parent().parent().parent().find('.workflow-wrap').last().clone(true).appendTo($(this).parent().parent().parent().parent().after());
      var elm = $(this).parent().parent().parent().parent().find('.workflow-wrap .input-wrap');
      var len = elm.length;

      var lastElm = elm.last();
      var lastLabel = lastElm.find('label').attr('for').replace(/[0-9]/g, len - 1);
      var lastId = lastElm.find('select').attr('id').replace(/[0-9]/g, len - 1);
      var lastName = lastElm.find('select').attr('name').replace(/[0-9]/g, len - 1);
      lastElm.find('select').val("");

      lastElm.find('label').attr('for', lastLabel);
      lastElm.find('select').attr('id', lastId);
      lastElm.find('select').attr('name', lastName);
    }
  });

  // Holiday Group select all link
  $(".holiday-select-link").click(function () {
    var year = $('#pills-tab').find('.active.show').text();
    $("#pills-tabContent").find('.year-' + year).prop('checked', true);
  });

  $(".btn-one").click(function () {
    $(".wrap-one").slideToggle();
  });

  $(".role-btn").click(function () {
    $(this).parent().nextAll('.' + $(this).attr('id')).toggle();
    $(this).find("i").toggleClass("rotate");
  });

  $(".checkAllParent").click(function () {
    checkboxFunc($(this), this);
  });

  $(".checkAllChild").click(function () {
    checkboxFunc($(this), this);
  });

  $(".check-parent-create").click(function () {
    checkboxFunc($(this), this);
  });

  $(".check-parent-update").click(function () {
    checkboxFunc($(this), this);
  });

  $(".check-parent-delete").click(function () {
    checkboxFunc($(this), this);
  });

  $(".check-parent-view").click(function () {
    checkboxFunc($(this), this);
  });

  function checkboxFunc($this1, $this2) {
    $('.' + $this1.attr('id')).not(this).prop('checked', $this2.checked);
  }

  // Sortable
  $("#sortable").sortable();
  $("#sortable").disableSelection();

  $("#sortable-two .remove-item").click(function () {
    $(this).parent().remove();
  });

  $('.list-block-wrap').hide();
  if ($('#sortable-two li').length >= 1) {
    $('.list-block-wrap').show();
  } else {
    $('.list-block-wrap').hide();
  }


  // Multiple Select option

  $('.label.ui.dropdown')
    .dropdown();

  $('.no.label.ui.dropdown')
    .dropdown({
      useLabels: false
    });

  $('.ui.button').on('click', function () {
    $('.ui.dropdown')
      .dropdown('restore defaults');
  });

  // Example 1.3: Sortable and connectable lists with visual helper
  $('#sortable-one, #sortable-two').sortable({
    connectWith: '#sortable-div .sortable-list',
    placeholder: 'placeholder',
    stop: function (event, ui) {

      $('.sortable-list').each(function () {

        var result = "";

        $(this).find("li").each(function () {
          var text = $(this).text().replace(/\s/g, "-") + ",";
          text = text.replace(/-remove/ig, "");
          result += text;
        });

        result = result.toLowerCase();

        $('.org-input').val(result);
      });
    }
  });

  // Textarea class adding
  $('textarea').addClass('mw-initial');


  //Process Late-entry Row clickable
  $(".clickable-row").click(function () {
    window.location = $(this).data("href");
  });


  // DatetimePicker Min and Max date range
  $(function () {

    $('#startdate, #enddate').datetimepicker({
      useCurrent: false,
      format: 'MM/DD/YYYY',
    });
    $('#startdate').datetimepicker().on('dp.change', function (e) {
      var incrementDay = moment(new Date(e.date));
      incrementDay.add(1, 'days');
      $('#enddate').data('DateTimePicker').minDate(incrementDay);
      $(this).data("DateTimePicker").hide();
    });

    $('#enddate').datetimepicker().on('dp.change', function (e) {
      var decrementDay = moment(new Date(e.date));
      decrementDay.subtract(1, 'days');
      $('#startdate').data('DateTimePicker').maxDate(decrementDay);
      $(this).data("DateTimePicker").hide();
    });

  });

  // Clone and Remove

  var regex = /^(.+?)(\d+)$/i;
  var cloneIndex = $(".clonedInput").length;

  var remove;

  function clone() {
    $(this).parents(".clonedInput").clone()
      .appendTo("body")
      .attr("id", "clonedInput" + cloneIndex)
      .find("*")
      .each(function () {
        var id = this.id || "";
        var match = id.match(regex) || [];
        if (match.length === 3) {
          this.id = match[1] + (cloneIndex);
        }
      })
      .on('click', 'a.clone', clone)
      .on('click', 'a.remove', remove);
    cloneIndex++;
  }

  function remove() {
    $(this).parents(".clonedInput").remove();
  }

  $("a.clone").on("click", clone);

  $("a.remove").on("click", remove);

  // Dashboard newDate
  var objToday = new Date(),
    domEnder = function () {
      var a = objToday;
      if (/1/.test(parseInt((a + "").charAt(0)))) return "";
      a = parseInt((a + "").charAt(1));
      return 1 == a ? "st" : 2 == a ? "nd" : 3 == a ? "rd" : ""
    }(),
    dayOfMonth = today + (objToday.getDate() < 10) ? '0' + objToday.getDate() + domEnder : objToday.getDate() + domEnder,
    months = new Array('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Augt', 'Sep', 'Oct', 'Nov', 'Dec'),
    curMonth = months[objToday.getMonth()],
    curYear = objToday.getFullYear();

  var today = dayOfMonth + "  " + curMonth + " " + curYear;
  $(".newDate").append(today);


});
