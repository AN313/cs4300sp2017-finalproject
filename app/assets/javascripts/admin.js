let crawlTimer;

function crawl(begin, end, index) {
  $.getJSON(
    `/admin/crawl?begin=${begin}&end=${end}&i=${index}`,
    (res) => {
      $('#crawl-status').html($('#crawl-status').html() + '\n' + res.name);
    });
}

$(document).ready(function() {
  $('select').material_select();

  $('#crawl-commit').click(function() {
    $('#crawl-commit').text('Running...');
    $('#crawl-status').html('');

    let surveyBegin = parseInt($('#crawl-begin').val(), 10);
    let surveyEnd = parseInt($('#crawl-end').val(), 10);
    let i = parseInt($('#crawl-resume').val(), 10);
    crawlTimer = setInterval(function() {
      crawl(surveyBegin, surveyEnd, i++);
      if (i > surveyEnd && crawlTimer) {
        clearInterval(crawlTimer);
        $('#crawl-commit').text('Start');
      }
    }, 5000);
  });

  $('#train-commit').click(function() {
    $('#train-commit').text('Running...');
    $('#train-status').html('');

    let trainBegin = parseInt($('#train-begin').val(), 10);
    let trainEnd = parseInt($('#train-end').val(), 10);
    let trainFunc = $('#train-func').val();

    $.getJSON(
      `/admin/train?begin=${trainBegin}&end=${trainEnd}&f=${trainFunc}`,
      (res) => {
        $('#train-status').html($('#train-status').html() + '\n' +
          res.name);
      });
  });
});
