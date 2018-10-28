// Define search url hover_text
var base_url = window.location.origin;

// Loading icon
var displayLoading = function() {
  // Display Loading Icon
  $('#query-button').hide();
  $('#loading').show();
}

var hideLoading = function() {
  // Hide loading
  $('#query-button').show();
  $('#loading').hide();
}

// Change active class on click in side bar
$(".nav li").on("click", function() {
    $(".nav li").removeClass("active");
    $(this).addClass("active");
});

// Request data: Plot Charts and Table Display
// var request_data_and_plot_charts = function(text, count) {
//   var params_url = "text=" + text + '&count=' + count;
//   var search_url = base_url + '/search?' + params_url;

//   $.get(search_url, function(obj, status) {

//     console.log('search',obj,'status',status);

//     // sentiLabels = ["Positive", "Negative", "Neutral"]
//     stanceLabels = ["Agree", "Disagree", "Discuss"]
//     // plot_pie_chart(obj['pie_chart_dataSentiment'], "piechartSentiment", sentiLabels);
//     // plot_line_chart(obj['line_chart_dataSentiment'], "linechartSentiment", sentiLabels);

//     plot_pie_chart(obj['pie_chart_dataStance'], "piechartStance", stanceLabels);
//     plot_line_chart(obj['line_chart_dataStance'], "linechartStance", stanceLabels);
//   });
// }

var plot_pie_chart = function(pie_chart_data, eleId, labelList) {
  console.log("Plotting pie chart", pie_chart_data);

  // color choice: see https://www.w3schools.com/colors/colors_rgb.asp
  var pos_count = pie_chart_data['pos'];
  var neg_count = pie_chart_data['neg'];
  var neu_count = pie_chart_data['neu'];

  var ctx1 = document.getElementById(eleId);
  var NewPieChart = new Chart(ctx1, {
    type: 'pie',
    data: {
      labels: labelList,
      datasets: [{
        label: "# of News",
        backgroundColor: ["#26af28", "#db2113", "#3e6cd8"],
        data: [ pos_count, neg_count, neu_count ]
      }]
    },
    options: {
      /*
      title: {
        display: true,
        text: 'Opinion Overview'
      },
      */
      legend: {
        display: true,
        labels: {
          fontSize: 12,
          fontColor: '#000000'
        }
      },
      layout: {
        padding: 50
      }
    }
  });
}

var plot_line_chart = function(line_chart_data, eleId, labelList) {
  console.log("Plotting line chart", line_chart_data)

  console.log(line_chart_data['date'])

  var ctx2 = document.getElementById(eleId);
  var NewLineChart = new Chart(ctx2, {
    type: 'line',
    data: {
      labels: line_chart_data['date'],
      datasets: [{
          data: line_chart_data['pos'],
          label: labelList[0],
          borderColor: "#26af28",
          fill: false
        }, {
          data: line_chart_data['neg'],
          label: labelList[1],
          borderColor: "#db2113", //c45850
          fill: false
        }, {
          data: line_chart_data['neu'],
          label: labelList[2],
          borderColor: "#3e6cd8",
          fill: false
        }
      ]
    },
    options: {
      /*
      title: {
        display: true,
        text: 'Opinion Over Time'
      },
      */
      scales: {
        xAxes: [{
          type: 'time',
          time: {
            displayFormats: {
              day: 'L'
            }
          }
        }]
      },
      legend: {
        display: true,
        labels: {
          fontSize: 12,
          fontColor: '#000000'
        }
      },
      layout: {
        padding: {
          top: 50
        }
      }
    }
  });

}

var page_data_to_table_display = function(text, count) {

  displayLoading();
  // if (stance == "Pos") { text = "支持"+text}
  // if (stance == "Neg") { text = "不支持"+text}

  var params_url = "text=" + text + '&count=' + count;
  var list_url = base_url + '/list?' + params_url;

  $.get(list_url, function(obj, status) {

    console.log('list',obj,'status',status);
    if ( status != 'success') {
      bootbox.alert("搜尋失敗！");
      hideLoading();
      return;
    }
    // plot pie & line chart
    // stanceLabels = ["Agree", "Disagree", "Discuss"]
    stanceLabels = ["Agree", "Disagree", "Neutral"]
    plot_pie_chart(obj['pie_chart_dataStance'], "piechartStance", stanceLabels);
    plot_line_chart(obj['line_chart_dataStance'], "linechartStance", stanceLabels);

    // Fill New Table Section
    var data = obj['json_data'];
    var table_body = $('#news-table').find('tbody');
    table_body.empty();

    for ( var news_id in data ) {
      var article = data[ news_id ];

      var date = article['date'];
      var id = article['id'];
      
      // var t_opi = article['t_opi'] == 'Positive' ? "正": (article['t_opi'] == 'Negative' ? "負" : "中");
      // var t_score = article['t_score'];
      // var t_font_color = article['t_opi'] == 'Positive' ? '#26af28': (article['t_opi'] == 'Negative' ? "#db2113" : "#3e6cd8");

      // var opi = article['opi'] == 'Positive' ? "正": (article['opi'] == 'Negative' ? "負" : "中");
      // var score = article['score'];
      // var font_color = article['opi'] == 'Positive' ? '#26af28': (article['opi'] == 'Negative' ? "#db2113" : "#3e6cd8");

      var title = article['title'];
      var url = article['url'];
      var website = article['website'];

      var stance = article['stance'];
      var stance_font_color = stance == 'agree' ? '#26af28': (stance == 'disagree' ? "#db2113" : "#3e6cd8");

      table_body.append(
          $('<tr>')
          .append( $('<td>').append(id) )
          .append( $('<td>').append( $('<a>').attr('href',url).attr('target','_blank').append(title)) )
          // .append( $('<td>').append( $('<font>').attr('color', t_font_color).append(t_opi)) )
          // .append( $('<td>').append( $('<font>').attr('color', t_font_color).append(t_score)) )
          // .append( $('<td>').append( $('<font>').attr('color', font_color).append(opi)) )
          // .append( $('<td>').append( $('<font>').attr('color', font_color).append(score)) )
          .append( $('<td>').append(website) )
          .append( $('<td>').append(date) )
          .append( $('<td>').append( $('<font>').attr('color', stance_font_color).append(stance)) )
        );
    }

    hideLoading();
  });

}

var handleSubmit = function() {
  //$("#query-button").on("click", function() {

  	var text = $('#query-input').val().trim();
    // var stance = $("input:checked")[0].value;
    // var count = $("input:checked")[1].value;
  	var count = $("input:checked")[0].value;

  // console.log('text:',text,'count:',count,'queryStance:',stance);
	console.log('text:',text,'count:',count);

	if ( !text || !count ) {
	  bootbox.alert("關鍵字輸入，選項請勿留白!");
	  return;
	}
	// request_data_and_plot_charts(text,count);
  // page_data_to_table_display(text,count,stance);
	page_data_to_table_display(text,count);
  //})
}

// Document ready function
$(document).ready(function() {
  console.log("Document ready!");

  $("#query-button").on("click", function() {
    handleSubmit()
  })

});
