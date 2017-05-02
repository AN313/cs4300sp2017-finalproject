$(document).ready(function() {

  $('#row-input').show();
  $('#row-prediction').hide();

  $("[name='classifier_type']").bootstrapSwitch();

  var classifier_type = "2";
  $("[name='classifier_type']").on('switchChange.bootstrapSwitch', function(
    e, state) {

    if (state) {
      classifier_type = "2";
      $('.non-textual').css('display', 'none');
    } else {
      classifier_type = "1";
      $('.non-textual').css('display', 'block');
    }

  });

  var amenities = [

    'Essentials',
    'Wifi',
    'Shampoo',
    'Closet/drawers',
    'TV',
    'Heat',
    'Air conditioning',
    'Breakfast, coffee, tea',
    'Desk/workspace',
    'Fireplace',
    'Iron',
    'Hair dryer',
    'Pets in the house',
    'Smoke detector',
    'Carbon monoxide detector',
    'First aid kit',
    'Safety card',
    'Fire extinguisher'

  ];

    amenities.forEach(function(item) {
      $('.modal-body').append(['<div class="checkbox">',
        '<label><input type="checkbox" ',
        'name="amenities" value="',
        item,
        '">',
        item,
        '</label></div>'
      ].join(''));
    });

  $('#sel-amenities').click(function() {
    $('#modal-sel-amenities input[type="checkbox"]').prop('checked',
      false);
    $('#modal-sel-amenities').modal();
  });

  $('#modal-sel-amenities-commit').click(function() {
    $('#amenities > div:last-child').html('');
    $('#modal-sel-amenities input[type="checkbox"]:checked').each(
      function() {
        $('#amenities > div:last-child').append([
          '<span class="label label-default">',
          $(this).val(),
          '</span>',
          ' '
        ].join(''));
      });
  });

//////////////////// RESULTS ///////////////////

  $('#btn-predict').click(function() {
    // get selected amenities
    var selected = [];
    $('.checkbox input:checked').each(function() {
      selected.push($(this).attr('value'));
    });
    // console.log(selected);
    var data = {};

    $('form').serializeArray().forEach(function(pair) {
      data[pair.name] = pair.value;
    });

    data['amenities'] = selected;
    data['classifier_type'] = classifier_type;

    //ajax call
    $.ajax({
      url: '/host/predict',
      type: 'post',
      data: JSON.stringify(data),
      contentType: 'application/json',
      dataType: 'json',
      success: function(t) {
        // Hide the form
        $('#row-input').hide();
        // Displayed the submitted info
        $('#row-prediction').show();

        // console.log(t.similar);
          price_html = '';
          var range;
          var prob;
          t.priceClass.forEach(function(entry) {
            range = entry['priceRange'];
            prob = entry['prob'];
            price_html += '<h3>'+ range + ' (' + prob + ')'+'</h3>';
          });
          $('#price_range').append(price_html);

        // Display result
        if (t.classifier_type === '1') {
          $('#toplowWords').hide();
          $('#reviewWords').hide();
          // $('#simtitle').hide();

        }else{

        

          // top words 
          word_html = '<div><h4>Most influenctial 10:</h4><ul class="close-words">';
          var word;
          var val;
          t.topWords.forEach(function(entry, i) {
            word = entry['word'];
            val = entry['val'];
            word_html += '<li>' +(i+1).toString()+ '. ' +word + ' (' + val + ')</li>\n'
          });
          word_html += '</ul></div>';


          // low words
          word_html += '<div><h4>Least influenctial 10:</h4><ul class="close-words">';
          t.lowWords.forEach(function(entry, i) {
            word = entry['word'];
            val = entry['val'];
            word_html += '<li>'+(i+1).toString()+'. ' + word + ' (' + val + ')</li>\n'
          });
          word_html += '</ul></div>';

          $('.sim-words').html(word_html);


          // top review words
          review_html = '<div><h4>Top 10 words in similar reviews:</h4><ul class="close-words">';
          t.reviewWords.forEach(function(entry,i) {
            word = entry['word'];
            val = entry['val'];
            review_html += '<li>' +(i+1).toString()+ '. ' +word + ' (' + val + ')</li>\n'
          });
          review_html += '</ul></div>';
          $('.review-words').html(review_html);

          }

        // similar listings 
        var sim_html = '';
        t.similar.forEach(function(entry, i) {
          // cut off last 5 characters since url contains '.json'
          var sim_url = [
            'http://www.',
            entry['url'].replace(/.json$/, '')
          ].join('');
          var pic_url = entry['picture_url'];
          var description = entry['description'];
          var sim_name = entry['name'];

          sim_html += [
            '<div class="box">',
            '<div class="wrap"><div>',
            '  <a href="',
            sim_url,
            '"><h3>',
            (i+1).toString() + '. ' + sim_name,
            '</h3></a>',
            '<div id="listing_des">',
            description,
            '</div>',
            '<img id=listing_pic src="',
            pic_url,
            '"></div>',
            '<div class="gradient"></div>',
            '</div>',
            '<div class="read-more"></div>',
            '</div>'
          ].join('');
        });


        $('#similar').append(sim_html);
        var slideHeight = 160;
        $(".box").each(function() {
            var $this = $(this);
            var $wrap = $this.children(".wrap");
            var $des_height = $this.find("#listing_des").height();
            var $pic_height = $this.find("#listing_pic").height();
            var $longer = $des_height > $pic_height ? $des_height : $pic_height;
            var defHeight = $wrap.height() + 10;
            if (defHeight >= slideHeight) {
                var $readMore = $this.find(".read-more");
                $wrap.css("height", slideHeight + "px");
                $readMore.append("<a href='#'>Click to Read More</a>");
                $readMore.children("a").bind("click", function(event) {
                    var curHeight = $wrap.height();
                    if (curHeight == slideHeight - 20) {
                        $wrap.animate({
                            height: defHeight
                        }, "normal");
                        $(this).text("Close");
                        $wrap.children(".gradient").fadeOut();
                    } else {
                        $wrap.animate({
                            height: slideHeight
                        }, "normal");
                        $(this).text("Click to Read More");
                        $wrap.children(".gradient").fadeIn();
                    }
                    return false;
            });
          }
        });

      }
    });
  });

  $('.non-textual').css('display', 'none');

});
