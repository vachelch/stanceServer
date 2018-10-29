// Define search url hover_text
var base_url = window.location.origin;

var handleFeedback = function(){
    label = $(this).attr('name')
    var this_node = $(this);
    var parent_tr = $(this).parent().parent()

    var query = parent_tr.find('._query-input').text()
    var url = parent_tr.find('._title a').attr('href')
    var title = parent_tr.find('._title').text()
    var website = parent_tr.find('._website').text()
    var date = parent_tr.find('._date').text()
    var stance = parent_tr.find('._stance').text()

    var data_json ={
        'query': query,
        'url': url,
        'title': title,
        'website': website,
        'date': date,
        'stance': stance,
        'label': label
    }

    var feedback_url = base_url + "/feedback";
    if (this_node.attr('class').includes('activate')){
        data_json['operation'] = 'delete';

        $.post(feedback_url, data_json, function(){
            this_node.removeClass('activate');
            this_node.siblings().removeClass('disactivate');
        });
    }
    else{
        data_json['operation'] = 'insert';

        $.post(feedback_url, data_json, function(){
            this_node.addClass('activate');
            this_node.siblings().addClass('disactivate');
        });
    }
}


// Change active class on click in side bar
$(".nav li").on("click", function() {
    $(".nav li").removeClass("active");
    $(this).addClass("active");
});


var dataset_to_table_display = function() {
  var list_url = base_url + '/feedback';

  $.get(list_url, function(data) {
    data = JSON.parse(data)
    // to see what the data look like
    // alert(JSON.stringify(data,null,'\t'))
    // alert(JSON.stringify(data[94],null,'\t'))

    // Fill New Table Section
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

      var query = article['query'];
      var title = article['title'];
      var url = article['url'];
      var website = article['website'];

      var stance = article['stance'];
      var label = article['label'];

      var stance_font_color = stance == 'agree' ? '#26af28': (stance == 'disagree' ? "#db2113" : "#3e6cd8");

      // label
      var label_td = $('<td>').addClass('_label');
      label_td.append($('<a>').attr('name', 'agree').attr('href', 'javascript:void(0);').addClass('agree').append('agree '));
      label_td.append($('<a>').attr('name', 'neutral').attr('href', 'javascript:void(0);').addClass('neutral').append('neutral '));
      label_td.append($('<a>').attr('name', 'disagree').attr('href', 'javascript:void(0);').addClass('disagree').append('disagree'));

      if (label != null){
          var activate_a = label_td.find('.' + label);
          activate_a.addClass('activate');
          activate_a.siblings().addClass('disactivate');
      }

      table_body.append(
          $('<tr>')
          .append( $('<td>').append(id) )
          .append( $('<td>').addClass('_query-input').append(query) )
          .append( $('<td>').addClass('_title').append( $('<a>').attr('href',url).attr('target','_blank').append(title)) )
          // .append( $('<td>').append( $('<font>').attr('color', t_font_color).append(t_opi)) )
          // .append( $('<td>').append( $('<font>').attr('color', t_font_color).append(t_score)) )
          // .append( $('<td>').append( $('<font>').attr('color', font_color).append(opi)) )
          // .append( $('<td>').append( $('<font>').attr('color', font_color).append(score)) )
          .append( $('<td>').addClass('_website').append(website) )
          .append( $('<td>').addClass('_date').append(date) )
          .append( $('<td>').addClass('_stance').append( $('<font>').attr('color', stance_font_color).append(stance)) )
          .append(label_td)
        );
    }

    $(".agree, .neutral, .disagree").on("click", handleFeedback);
  });

}


// Document ready function
$(document).ready(function() {
  console.log("Document ready!");

  $("#labeled_data").on("click", dataset_to_table_display);
  $("#labeled_data").click();
});




























