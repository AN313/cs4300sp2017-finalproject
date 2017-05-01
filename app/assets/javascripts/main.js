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

  // $('.modal-body').html(
  //   '<label for="amenities">What amenities do you offer?</label>');
    amenities.forEach(function(item) {
      $('.modal-body').append(['<div class="checkbox">',
        '<label><input type="checkbox" ',
        'name="amenities" value="',
        item,
        '">',
        item,
        '</label></div>'
      ].join(''));
      // console.log("in amenitiy appending");
    });

  
  $('#btn-predict').click(function() {
    
    var selected = [];
    $('.checkbox input:checked').each(function() {
      selected.push($(this).attr('value'));
    });
    console.log(selected);
    var data = {};

    $('form').serializeArray().forEach(function(pair) {
      data[pair.name] = pair.value;
    });

    data['amenities'] = selected;
    data['classifier_type'] = classifier_type;


    console.log(data);
    console.log(JSON.stringify(data));

    $.ajax({
      url: '/host/predict',
      type: 'post',
      data: JSON.stringify(data),
      contentType: 'application/json',
      dataType: 'json',
      success: function(t) {
        console.log(data);
        // Hide the form
        $('#row-input').hide();
        // Displayed the submitted info
        $('#row-prediction').show();


        // Display result
        if (t.classifier_type === '1') {
          $('#simtitle').hide();
          $('#wordsTitle').hide();
        }

        $('#price_range').html(['<h2>', '$', t.priceClass,
          '</h2>'
        ].join(''));

        $('#topWords').html(['<p>', t.topWords, '</p>'].join(''));


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
            i.toString() + '. ' + sim_name,
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
        var slideHeight = 200;
        $('.box').each(function() {
          var $this = $(this);
          var $wrap = $this.children(".wrap");
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
