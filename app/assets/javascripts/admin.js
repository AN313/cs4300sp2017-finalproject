let crawlTimer;

function crawl(begin, end, index) {
  $.getJSON(
    `/admin/crawl?begin=${begin}&end=${end}&i=${index}`,
    (res) => {
      $('#crawl-status').html($('#crawl-status').html() + '\n' + res.name);
    });
}

$(document).ready(function() {

  $('#crawl-commit').click(function() {
    $('#crawl-commit').text('Running...');
    let surveyBegin = parseInt($('#crawl-begin').val(), 10);
    let surveyEnd = parseInt($('#crawl-end').val(), 10);
    let i = surveyBegin;
    crawlTimer = setInterval(function() {
      crawl(surveyBegin, surveyEnd, i++);
      if (i > surveyEnd && crawlTimer) {
        clearInterval(crawlTimer);
        $('#crawl-commit').text('Start');
      }
    }, 5000);
  });
});
