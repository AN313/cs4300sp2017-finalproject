$(document).ready(function() {
  $('#row-input').show();
  $('#row-prediction').hide();

  $('[name="classifier_type"]').bootstrapSwitch();

  var classifier_type = '2';
  $('[name="classifier_type"]').on('switchChange.bootstrapSwitch', function(
    e, state) {
    if (state) {
      classifier_type = '2';
      $('.non-textual').css('display', 'none');
    } else {
      classifier_type = '1';
      $('.non-textual').css('display', 'block');
    }

  });

  // add amenities dynamically
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

  $('.modal-body').html(
    '<label for="amenities">What amenities do you offer?</label>');
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

  $('#btn-predict').click(function() {
    var selected = [];
    $('.checkbox input:checked').each(function() {
      selected.push($(this).attr('value'));
    });

    var data = {};

    $('form').serializeArray().forEach(function(pair) {
      data[pair.name] = pair.value;
    });

    data['amenities'] = selected;
    data['classifier_type'] = classifier_type;

    $.ajax({
      url: '/host/predict',
      type: 'post',
      data: JSON.stringify(data),
      contentType: 'application/json',
      dataType: 'json',
      success: function(response) {
        // Hide the form
        $('#row-input').hide();
        // Displayed the submitted info
        $('#row-prediction').show();


        // Display result
        var type = Object.entries(response)[2][1];

        if (type == '1') {
          $('#simtitle').hide();
          $('#wordsTitle').hide();
        }

        var price = Object.entries(response)[0][1];
        var p = document.createTextNode('$' + price);
        var h = document.createElement('h2');
        h.appendChild(p);
        document.getElementById('price_range').appendChild(h);


        var topWords = Object.entries(response)[3][1];
        var words = document.createTextNode(topWords);
        var pa = document.createElement('p');
        pa.appendChild(words);
        document.getElementById('topWords').appendChild(pa);


        var similar = Object.entries(response)[1][1];

        var sim_html = '';
        var i = 1;
        similar.forEach(function(entry) {
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
          i += 1;
        });


        document.getElementById('similar').innerHTML += sim_html;
        var slideHeight = 200;
        $('.box').each(function() {
          var $this = $(this);
          var $wrap = $this.children('.wrap');
          var defHeight = $wrap.height() + 10;
          if (defHeight >= slideHeight) {
            var $readMore = $this.find('.read-more');
            $wrap.css('height', slideHeight + 'px');
            $readMore.append(
              '<a href="#">Click to Read More</a>');
            $readMore.children('a').bind('click', function() {
              var curHeight = $wrap.height();
              if (curHeight == slideHeight - 20) {
                $wrap.animate({
                  height: defHeight
                }, 'normal');
                $(this).text('Close');
                $wrap.children('.gradient').fadeOut();
              } else {
                $wrap.animate({
                  height: slideHeight
                }, 'normal');
                $(this).text('Click to Read More');
                $wrap.children('.gradient').fadeIn();
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
