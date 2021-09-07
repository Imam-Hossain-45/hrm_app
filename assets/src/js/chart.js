var months = [
  'Jan',
  'Feb',
  'Mar',
  'Apr',
  'May',
  'Jun',
  'Jul',
  'Aug',
  'Sep',
  'Oct',
  'Nov',
  'Dec'
];
var days = [
  'Sunday',
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday'
];

function get_employee_count_chart(res) {
  var maleEmp = res.employee_count.male;
  var femaleEmp = res.employee_count.female_employee;
  var otherEmp = res.employee_count.other_employee;

  var empTotal = maleEmp + femaleEmp + otherEmp;

  $(".cmp-count").html(empTotal);
  var employeeCount = document.getElementById("empCountChart");

  if (employeeCount) {
    employeeCount = employeeCount.getContext('2d');
    var lineChart = new Chart(employeeCount, {

      type: 'doughnut',
      data: {
        labels: ['Male', 'Female', 'Others'],
        datasets: [{
          data: [maleEmp, femaleEmp, otherEmp],
          backgroundColor: [
            'rgba(255, 99, 132, 0.9)',
            'rgba(113, 106, 202, 0.9)',
            'rgba(255, 206, 86, 0.9)'
          ]
        }]
      },
      options: {
        scales: {
          yAxes: [{
            ticks: {
              display: false
            },
            gridLines: {
              display: false,
            }
          }]
        },
        legend: {
          display: true,
          position: 'bottom',
        },
        title: {
          display: true,
          text: 'Employee Count'
        }
      }
    });
  }
}

// Employee Daily attandance
function get_today_attendance_info(res) {
  var todayPresent = res.today_attendance.is_present;
  var todayLate = res.today_attendance.is_late;

  if (todayPresent == true && todayLate == false) {
    $(".present-div").show();
  } else {
    $(".present-div").hide();
  }

  if (todayLate == true) {
    $(".late-div").show();
  } else {
    $(".late-div").hide();
  }

  var attnTime = res.today_attendance.in_time;

  var splittedValue = attnTime.split(':');
  var time = splittedValue[0];
  var amPm = 'PM';
  if (time < 12) {
    amPm = ' AM';
  }
  var formattedTime = splittedValue[0] + ':' + splittedValue[1];
  var formattedAMPM = amPm;

  $(".theTime").append(formattedTime);
  $("p.sup").append(formattedAMPM);
}

// Daily attandance status
function daily_attendance_info(res) {
  var dailyPresent = res.date_wise_attendance.present;
  var dailyLate = res.date_wise_attendance.late;
  var dailyLeave = res.date_wise_attendance.leave;
  var dailyAbsent = res.date_wise_attendance.absent;

  $(".present-total").append(dailyPresent);
  $(".late-total").append(dailyLate);
  $(".leave-total").append(dailyLeave);
  $(".absent-total").append(dailyAbsent);
}

// Employee Personal Calendar 
function get_personal_calendar_info(res) {

  var calendarEvents = res.calendars;
  var events = [];
  for (i = 0; i < calendarEvents.length; i++) {
    events.push({
      startDate: calendarEvents[i].start_date,
      endDate: calendarEvents[i].end_date,
      summary: calendarEvents[i].name
    });
  }

  $("#event-calendar").simpleCalendar({
    fixedStartDay: false,
    disableEmptyDetails: true,
    events: events,
  });
}

// Notice board
function get_notice_board(res) {
  var notice = res.noticeboards;
  var html = '';
  var months = [
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec'
  ];
  var days = [
    'Sunday',
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday'
  ];

  for (var i = 1; i < notice.length; i++) {
    var dateTime = new Date(notice[i].published_datetime);
    var published_datetime = dateTime.getDate() + ' ' + months[dateTime.getMonth()] + ' - ' + days[dateTime.getDay()];
    var startDateTime = new Date(notice[i].start_date);
    var endDateTime = new Date(notice[i].end_date);
    var start_date = startDateTime.getDate() + ' ' + months[startDateTime.getMonth()];
    var end_date = endDateTime.getDate() + ' ' + months[endDateTime.getMonth()];
    var timing = ' from ' + start_date + ' to ' + end_date;

    if (notice[i].start_date == notice[i].end_date) {
      timing = ' on ' + end_date;
    }

    html += '<div class="comment-wrap d-flex">' +
      '  <div class="comment-info">' +
      '    <h2 class="dash-title">' + notice[i].notice + '<span>' + timing + '</span>' +
      '    </h2>' +
      '    <p class="dash-date">' + published_datetime + '</p>' +
      '  </div>' +
      '</div>';
  }

  $('#notice-board').html(html);
  if (notice[0].counter > 3) {
    $("#notice-show").show();
  }
}

// Notifications
function get_notifications(res) {
  var notification = res.notifications;
  var html = '';
  var months = [
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec'
  ];
  var days = [
    'Sunday',
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday'
  ];

  for (var i = 0; i < notification.length; i++) {
    var dateTime = new Date(notification[i].created_at);
    var published_datetime = dateTime.getDate() + ' ' + months[dateTime.getMonth()] + ' - ' + days[dateTime.getDay()];

    html += '<div class="comment-wrap d-flex">' +
      '  <div class="comment-info">' +
      '    <h2 class="dash-title">' + notification[i].content +
      '    </h2>' +
      '    <p class="dash-date">' + published_datetime + '</p>' +
      '  </div>' +
      '</div>';
  }

  $('#notification-board').html(html);
}

// Approvals
function get_approvals(res) {
  var approvals = res.approvals;
  var html = '';


  for (var i = 0; i < approvals.length; i++) {
    var empName = approvals[i].applied_by;
    var appliedDuration = approvals[i].duration;
    var appliedFor = approvals[i].applied_for;
    var dateTime = new Date(approvals[i].created_at);

    var startDateTime = new Date(approvals[i].application_start_date);
    var endDateTime = new Date(approvals[i].application_end_date);
    var start_date = startDateTime.getDate() + ' ' + months[startDateTime.getMonth()];
    var end_date = endDateTime.getDate() + ' ' + months[endDateTime.getMonth()];
    var timing = ' from ' + start_date + ' to ' + end_date;

    var leaveLink = '';

    if (approvals[i].application_type == "leave") {
      leaveLink = '/admin/leave/process/leave_approval/' + approvals[i].id;
    } else if (approvals[i].application_type == "late-entry") {
      leaveLink = '/admin/attendance/process/late_entry_approval/' + approvals[i].id;
    } else if (approvals[i].application_type == "early-out") {
      leaveLink = '/admin/attendance/process/early_out_approval/' + approvals[i].id;
    }

    if (approvals[i].start_date == approvals[i].end_date) {
      timing = ' on ' + end_date;
    }

    var published_datetime = dateTime.getDate() + ' ' + months[dateTime.getMonth()] + ' - ' + days[dateTime.getDay()];

    html += '<a href="' + leaveLink + '">' +
      '<div class="comment-wrap d-flex">' +
      '<img class="comment-img" src="https://avatars3.githubusercontent.com/u/1071625?s=460&v=4" alt="">' +
      '  <div class="comment-info">' +
      '    <h2 class="dash-title">' + empName +
      '    <span>has applied for' + appliedDuration + ' of ' + appliedFor + timing + '</span>' +
      '    </h2>' +
      '    <p class="dash-date">' + published_datetime + '</p>' +
      '  </div>' +
      '</div>' +
      '</a>';
  }

  var pending_items = approvals.length;

  $('#approvals').html(html);
  $('.pending-items span').append(pending_items);
}

// Salarywise Breakdown
function get_salarywise_breakdown(res) {

  var salaryBreakdown = res.salary_wise_breakdowns;
  var labels = [];
  var data = [];

  for (var i = 0; i < salaryBreakdown.length; i++) {
    labels.push(salaryBreakdown[i].from + ' - ' + salaryBreakdown[i].to);
    data.push(salaryBreakdown[i].total);
  }

  var employeeSalary = document.getElementById('empSalaryChart');

  if (employeeSalary) {
    employeeSalary = employeeSalary.getContext('2d');
    var empSalaryChart = new Chart(employeeSalary, {
      type: 'polarArea',
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: [
            'rgba(255, 99, 132, 0.9)',
            'rgba(113, 106, 202, 0.9)',
            'rgba(255, 206, 86, 0.9)',
            'rgba(75, 192, 192, 0.9)',
            'rgba(153, 102, 255, 0.9)'
          ],
        }]
      },
      options: {
        scales: {
          yAxes: [{
            ticks: {
              display: false
            },
            gridLines: {
              display: false,
            }
          }]
        },
        legend: {
          display: true,
          position: 'bottom',
          labels: {
            fontColor: '#666'
          }
        },
        title: {
          display: true,
          text: 'Employee Count'
        }
      }
    });
  }

}

// Employee Leave Credit
function employee_leave_credit(res) {
  var credits = res.leave_credit;
  var html = '';


  for (var i = 0; i < credits.length; i++) {
    var leaveName = credits[i].leave_name;
    var leaveCredit = credits[i].credit;
    var leaveAvail = credits[i].avail;
    var leaveRemaining = credits[i].remaining;

    html += '<tr>' +
      '    <td>' + leaveName + '</td>' +
      '    <td class="text-center">' + leaveCredit.match(/\d+/) + '</td>' +
      '    <td class="text-center">' + leaveAvail.match(/\d+/) + '</td>' +
      '    <td class="text-center">' + leaveRemaining.match(/\d+/) + '</td>' +
      '    </tr>';
  }

  $('#leave-credit').html(html);

}

// Employee Attendance statistics
function get_employee_attendance_statistics(res) {
  var dates = [];
  var labels = [];
  var data = [];
  var bacColors = [];
  var credits = res.attendance_statistics;
  var minTime = new Date(credits[0].in_date + ' 00:00:00').getTime();
  var maxTime = new Date(credits[0].in_date + ' 23:59:00').getTime();

  for (var i = 0; i < credits.length; i++) {
    var startDateTime = new Date(credits[i].in_date);
    var inDate = startDateTime.getDate();

    if (credits[i].is_late) {
      bacColors.push('red');
    } else if (credits[i].early_out_value > 0) {
      bacColors.push('orange');
    } else {
      bacColors.push('green');
    }

    dates.push(credits[i].in_date);
    labels.push(inDate);
    data.push(new Date(credits[0].in_date + ' ' + credits[i].in_time).getTime());
  }

  var atnStatistics = document.getElementById('atnStatisticsChart');

  if (atnStatistics) {
    atnStatistics = atnStatistics.getContext('2d');
    var atnStatisticsChart = new Chart(atnStatistics, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: ['Late', 'On Time', 'Early Out'],
          data: data,
          backgroundColor: bacColors,
        }]
      },
      options: {
        scales: {
          yAxes: [{
            ticks: {
              display: true,
              callback: function (value, index, labels) {
                var date = new Date(value);
                var hours = date.getHours();
                var minutes = date.getMinutes();
                var ampm = hours >= 12 ? 'pm' : 'am';
                hours = hours % 12;
                hours = hours ? hours : 12;
                minutes = minutes < 10 ? '0' + minutes : minutes;
                var strTime = hours + ':' + minutes + ' ' + ampm;
                return strTime;
              },
              stepSize: 10000000,
              min: minTime,
              max: maxTime
            },
            gridLines: {
              display: true,
            }
          }]
        },
        tooltips: {
          callbacks: {
            label: function (tooltipItem, data) {
              var status;
              var background = data.datasets[0].backgroundColor[tooltipItem.index];
              var date = new Date(parseInt(data.datasets[0].data[tooltipItem.index], 10));
              var hours = date.getHours();
              var minutes = date.getMinutes();
              var ampm = hours >= 12 ? 'pm' : 'am';
              hours = hours % 12;
              hours = hours ? hours : 12;
              minutes = minutes < 10 ? '0' + minutes : minutes;
              var strTime = hours + ':' + minutes + ' ' + ampm;

              switch (background) {
                case 'red':
                  status = 'Late';
                  break;
                case 'green':
                  status = 'On Time';
                  break;
                default:
                  status = 'Early Out';
              }

              return strTime + ' - ' + status;
            }
          }
        },
        legend: {
          display: true,
          position: 'top',
        },
        title: {
          display: false,
          text: 'Attendance Statistics'
        }
      }
    });
  }
}

// Late Early Out Underwork
function employee_yearly_status(res) {
  var data = [];
  var data1 = [];
  var data2 = [];
  var bacColorsL = [];
  var bacColorsR = [];
  var bacColorsU = [];
  var status = res.yearly_status;

  for (var i = 0; i < status.length; i++) {
    if (status[i].count_late > 0) {
      bacColorsL.push('red');
    } else if (status[i].count_early_out > 0) {
      bacColorsR.push('orange');
    } else {
      bacColorsU.push('green');
    }

    data.push(status[i].count_late);
    data1.push(status[i].count_early_out);
    data2.push(status[i].count_under_work);
  }

  var yearlyAtnStatistics = document.getElementById('yearlyAtnStatisticsChart');

  if (yearlyAtnStatistics) {
    yearlyAtnStatistics = yearlyAtnStatistics.getContext('2d');
    var yearlyAtnStatisticsChart = new Chart(yearlyAtnStatistics, {
      type: 'bar',
      data: {
        labels: months,
        datasets: [{
            label: 'Late',
            data: data,
            backgroundColor: 'red',
          },
          {
            label: 'Early Out',
            data: data1,
            backgroundColor: 'orange',
          },
          {
            label: 'Underwork',
            data: data2,
            backgroundColor: 'green',
          }
        ]
      },
      options: {
        scales: {
          yAxes: [{
            ticks: {
              display: false,
            },
            gridLines: {
              display: false,
            }
          }]
        },
        legend: {
          display: true,
          position: 'top',
        },
        title: {
          display: false,
          text: 'Attendance Statistics'
        }
      }
    });
  }
}

// Payment Disbursment
function get_payment_disbursment(res) {
  var data = [];
  var payDisbursment = res.payment_disbursements;

  var payables = payDisbursment[0].amount;
  $('#payables span').append(payables);

  for (var i = 0; i < payDisbursment.length; i++) {
    var DateTime = new Date(payDisbursment[i].date);

    data[DateTime.getMonth()] = payDisbursment[i].amount;
  }

  var paymentDisbursement = document.getElementById('myChart');

  if (paymentDisbursement) {
    paymentDisbursement = paymentDisbursement.getContext('2d');
    var myChart = new Chart(paymentDisbursement, {
      type: 'bar',
      data: {
        labels: months,
        datasets: [{
          label: 'Y 2020',
          data: data,
          backgroundColor: [
            'rgba(255, 99, 132, 0.2)',
            'rgba(54, 162, 235, 0.2)',
            'rgba(255, 206, 86, 0.2)',
            'rgba(75, 192, 192, 0.2)',
            'rgba(153, 102, 255, 0.2)',
            'rgba(255, 159, 64, 0.2)',
            'rgba(255, 99, 132, 0.2)',
            'rgba(54, 162, 235, 0.2)',
            'rgba(255, 206, 86, 0.2)',
            'rgba(75, 192, 192, 0.2)',
            'rgba(153, 102, 255, 0.2)',
            'rgba(255, 159, 64, 0.2)',
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)',
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)',
          ],
          borderWidth: 1
        }]
      },
      options: {
        scales: {
          yAxes: [{
            ticks: {
              display: false
            },
            gridLines: {
              display: false,
            }
          }]
        },
        legend: {
          position: 'top',
          labels: {
            fontColor: '#666'
          }
        }
      }
    });
  }
}

// Admin Daily attendance chart
function get_daily_attendance(res) {
  var daywiseAttendance = res.date_wise_attendance;

  var present = daywiseAttendance.present;
  var late = daywiseAttendance.late;
  var leave = daywiseAttendance.leave;
  var absent = daywiseAttendance.absent;


  var dailyAttandance = document.getElementById('dailyAttandanceChart');

  if (dailyAttandance) {
    dailyAttandance = dailyAttandance.getContext('2d');
    var dailyAttandanceChart = new Chart(dailyAttandance, {
      type: 'doughnut',
      data: {
        labels: ['Present On Time', 'Late', 'Leave', 'Absent'],
        datasets: [{
          data: [present, late, leave, absent],
          backgroundColor: [
            'rgba(255, 99, 132, 0.9)',
            'rgba(113, 106, 202, 0.9)',
            'rgba(255, 206, 86, 0.9)',
            'rgba(113, 106, 202, 0.9)'
          ]
        }]
      },
      options: {
        scales: {
          yAxes: [{
            ticks: {
              display: false
            },
            gridLines: {
              display: false,
            }
          }]
        },
        legend: {
          display: true,
          position: 'bottom',
        }
      }
    });
  }
}

// Monthly Attendance Chart
function get_monthly_attendance(res) {
  var labels = [];
  var data1 = [];
  var data2 = [];
  var data3 = [];
  var data4 = [];
  var monthlyAttendance = res.month_wise_attendance;

  for (var i = 0; i < monthlyAttendance.length; i++) {
    var DateTime = new Date(monthlyAttendance[i].date);
    var inDate = DateTime.getDate();

    data1.push(monthlyAttendance[i].present);
    data2.push(monthlyAttendance[i].late);
    data3.push(monthlyAttendance[i].leave);
    data4.push(monthlyAttendance[i].absent);
    labels.push(inDate);
  }


  var monthlyAttandance = document.getElementById('monthlyAttandanceChart');

  if (monthlyAttandance) {
    monthlyAttandance = monthlyAttandance.getContext('2d');

    var monthlyAttandanceChart = new Chart(monthlyAttandance, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          data: data1,
          label: "Present",
          borderColor: "#3e95cd",
          fill: false
        }, {
          data: data2,
          label: "Late",
          borderColor: "#8e5ea2",
          fill: false
        }, {
          data: data3,
          label: "Leave",
          borderColor: "#3cba9f",
          fill: false
        }, {
          data: data4,
          label: "Absent",
          borderColor: "#e8c3b9",
          fill: false
        }]
      },
      options: {
        title: {
          display: true,
          text: 'Monthly Trend',
        },
        legend: {
          display: false,
          position: 'bottom',
        }
      }
    });
  }
}

// Datewise leave Chart
function get_datewise_leave(res) {
  var labels = [];
  var data = [];
  var daywiseLeave = res.date_wise_leave;
  var leaveType = daywiseLeave.leaves;

  // console.log(leaveType);

  for (var i = 0; i < leaveType.length; i++) {

    labels.push(leaveType[i].leave_type);
    data.push(leaveType[i].availed);
  }

  // console.log(labels, data);

  var dailyLeave = document.getElementById('dailyLeaveChart');

  if (dailyLeave) {
    dailyLeave = dailyLeave.getContext('2d');
    var dailyLeaveChart = new Chart(dailyLeave, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: [
            'rgba(255, 99, 132, 0.9)',
            'rgba(113, 106, 202, 0.9)',
            'rgba(255, 206, 86, 0.9)',
            'rgba(113, 106, 202, 0.9)'
          ]
        }]
      },
      options: {
        scales: {
          yAxes: [{
            ticks: {
              display: false
            },
            gridLines: {
              display: false,
            }
          }]
        },
        legend: {
          display: true,
          position: 'bottom',
        },
        title: {
          display: true,
          text: 'Leave in Daily View'
        }
      }
    });
  }
}

// Monthwise leave Chart
function get_monthwise_leave(res) {
  var dates = [];
  var data1 = [];
  var data2 = [];
  var data3 = [];
  var data4 = [];
  var monthwiseLeave = res.month_wise_leave;
  console.log(monthwiseLeave);

  for (var i = 0; i < dateTime.length; i++) {
    var DateTime = new Date(monthwiseLeave.date);
    var inDate = DateTime.getDate();
    console.log(inDate);

    data1.push(monthwiseLeave[i].present);
    data2.push(monthwiseLeave[i].late);
    data3.push(monthwiseLeave[i].leave);
    data4.push(monthwiseLeave[i].absent);
    labels.push(inDate);
  }

  for (var i = 0; i < monthwiseLeave.length; i++) {
    var DateTime = new Date(monthwiseLeave.date);
    var inDate = DateTime.getDate();
    console.log(inDate);

    data1.push(monthwiseLeave[i].present);
    data2.push(monthwiseLeave[i].late);
    data3.push(monthwiseLeave[i].leave);
    data4.push(monthwiseLeave[i].absent);
    labels.push(inDate);
  }

  console.log("this", labels);


  var monthlyLeave = document.getElementById('monthlyLeaveChart');

  if (monthlyLeave) {
    monthlyLeave = monthlyLeave.getContext('2d');

    var monthlyLeaveChart = new Chart(monthlyLeave, {
      type: 'line',
      data: {
        labels: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
        datasets: [{
          data: [10, 20, 30, 20, 10, 15, 20, 30, 10, 20, 30, 20, 10, 15, 20, 30, 20, 10, 15, 30, 41, 52, 43, 24, 25, 26, 27, 28, 29, 30, 31],
          label: "A",
          borderColor: "#3e95cd",
          fill: false
        }, {
          data: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
          label: "B",
          borderColor: "#8e5ea2",
          fill: false
        }, {
          data: [43, 24, 25, 26, 27, 28, 29, 30, 31, 10, 20, 30, 40, 50, 60, 56, 37, 68, 79, 30, 51, 62, 43, 24, 25, 26, 27, 28, 29, 30, 31, 10, 20, 30, 40, 50, 60, 70, 20, 15, 20, 71, 62, 53, 74, 65],
          label: "C",
          borderColor: "#3cba9f",
          fill: false
        }, {
          data: [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, ],
          label: "C",
          borderColor: "#e8c3b9",
          fill: false
        }]
      },
      options: {
        title: {
          display: true,
          text: 'Monthly Trend',
        },
        legend: {
          display: false,
          position: 'bottom',
        }
      }
    });
  }
}


$(document).ready(function () {
  $.ajax({
    type: 'GET',
    url: 'http://localhost:8000/api/dashboard/',
    success: function (res) {
      if (res.employee_count) {
        get_employee_count_chart(res);
      }

      if (res.calendars) {
        get_personal_calendar_info(res);
      }

      if (res.noticeboards) {
        get_notice_board(res);
      }

      if (res.notifications) {
        get_notifications(res);
      }

      if (res.approvals) {
        get_approvals(res);
      }

      if (res.salary_wise_breakdowns) {
        get_salarywise_breakdown(res);
      }

      if (res.leave_credit) {
        employee_leave_credit(res);
      }

      if (res.date_wise_attendance) {
        daily_attendance_info(res);
      }

      if (res.attendance_statistics) {
        get_employee_attendance_statistics(res);
      }

      // Yearly Late, Early Out, Underwork
      if (res.yearly_status) {
        employee_yearly_status(res);
      }

      // Payment Disbursment
      if (res.payment_disbursements) {
        get_payment_disbursment(res);
      }

      // Daily attendance chart
      if (res.date_wise_attendance) {
        get_daily_attendance(res);
      }

      // Monthly Attendance chart
      if (res.month_wise_attendance) {
        get_monthly_attendance(res);
      }

      //Daily attendance status
      if (res.today_attendance) {
        get_today_attendance_info(res);
      }

      // Datewise leave
      if (res.date_wise_leave) {
        get_datewise_leave(res);
      }



      //Daily Leave chart
      // var dailyLeave = document.getElementById('dailyLeaveChart');

      // if (dailyLeave) {
      //   dailyLeave = dailyLeave.getContext('2d');
      //   var dailyLeaveChart = new Chart(dailyLeave, {
      //     type: 'doughnut',
      //     data: {
      //       labels: ['Male', 'Female', 'Others'],
      //       datasets: [{
      //         data: [65, 30, 5],
      //         backgroundColor: [
      //           'rgba(255, 99, 132, 0.9)',
      //           'rgba(113, 106, 202, 0.9)',
      //           'rgba(255, 206, 86, 0.9)'
      //         ]
      //       }]
      //     },
      //     options: {
      //       scales: {
      //         yAxes: [{
      //           ticks: {
      //             display: false
      //           },
      //           gridLines: {
      //             display: false,
      //           }
      //         }]
      //       },
      //       legend: {
      //         display: false,
      //         position: 'bottom',
      //       },
      //       title: {
      //         display: true,
      //         text: 'Leave in Daily View'
      //       }
      //     }
      //   });
      // }


      // Yearly Leave chart
      var yearlyLeave = document.getElementById('yearlyLeaveChart');

      if (yearlyLeave) {
        yearlyLeave = yearlyLeave.getContext('2d');

        var yearlyLeaveChart = new Chart(yearlyLeave, {
          type: 'radar',
          data: {
            labels: ["Africa", "Asia", "Europe", "Latin America", "North America"],
            datasets: [{
              label: "1950",
              fill: true,
              backgroundColor: "rgba(179,181,198,0.2)",
              borderColor: "rgba(179,181,198,1)",
              pointBorderColor: "#fff",
              pointBackgroundColor: "rgba(179,181,198,1)",
              data: [8.77, 55.61, 21.69, 6.62, 6.82]
            }, {
              label: "2050",
              fill: true,
              backgroundColor: "rgba(255,99,132,0.2)",
              borderColor: "rgba(255,99,132,1)",
              pointBorderColor: "#fff",
              pointBackgroundColor: "rgba(255,99,132,1)",
              pointBorderColor: "#fff",
              data: [25.48, 54.16, 7.61, 8.06, 4.45]
            }]
          },
          options: {
            title: {
              display: true,
              text: 'Leave in Year View'
            },
            legend: {
              display: false,
              position: 'bottom',
            }
          }
        });
      }
    }
  });


});
