function search(urlAddress, data) {
  var searchValue = $.trim($(data).val());
  $.ajax({
      type: "GET",
      url: urlAddress,
      dataType: "json",
      data: {search_text: searchValue},
      success: function (result) {
        $('.search-result').css('display', 'block');
        var employee = '';

        // get employee data
        $.each(result.employee_list, function (employeeData) {
          if(data == "#search"){
              employee += "<li>";
              employee += "<a href='?query=" + result.employee_list[employeeData].id + "'>";
              employee += "<p>" + result.employee_list[employeeData].name + "</p>";
              employee += "<p>" + result.employee_list[employeeData].employee_id + "</p>";
              employee += "<p>" + result.employee_list[employeeData].designation + "</p>";
              employee += "</a>";
              employee += "</li>";
          }else{
              employee += "<li>";
              employee += "<input type='hidden' value='"+ result.employee_list[employeeData].id + "'>";
              employee += "<p>" + result.employee_list[employeeData].name + "</p>";
              employee += "<p>" + result.employee_list[employeeData].employee_id + "</p>";
              employee += "<p>" + result.employee_list[employeeData].designation + "</p>";
              employee += "</li>";
            }
        });
        // employee data append
        if (employee != '') {
          $('.search_employee').empty();
          $('.search_employee').append(employee);
        } else {
          employee += '<li>No Employee Found</li>';
          $('.search_employee').empty();
          $('.search_employee').append(employee);
        }
      }
      });
}
/**
 * Check http request method.
 * *
 * @param method
 * @returns {*|boolean}
 **/
function csrfSafeMethod(method) {
  // These HTTP method do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

/**
 * Get the csrf token.
 *
 * @returns {*|jquery|*|*|*|*}
 * **/
function csrftoken() {
  return $("[name=csrfmiddlewaretoken]").val();
}

$(document).ready(function () {
  /**
   *Setup ajax so that it always sends csrf token header.
   **/
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader('X-CSRFToken', csrftoken())
      }
    }
  });


  $('#search').on("paste keyup", function () {
    search("leave_entry_search/", "#search");
  });

  $('#employee_search').on("paste keyup", function () {
    search("leave_entry_search/", "#employee_search");
  });

});

$(document).on('click', '#search_employee li', function(){
   $('#employee_search').val($(this).text());
   $('#query').val($(this).find("input").val());
   $('#search_employee').fadeOut();
});
