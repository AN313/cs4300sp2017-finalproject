$(document).ready(function() {

  console.log('lalala good js');

  $('#row-input').show();
  $('#row-prediction').hide();

  $("[name='classifier_type']").bootstrapSwitch();

  var classifier_type = "2";
  $("[name='classifier_type']").on('switchChange.bootstrapSwitch', function(e, state) {
    //console.log("what");
    if (state) {
      classifier_type = "2";
      $('.non-textual').css('display', 'none');
    } else {
      classifier_type = "1";
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
      console.log("in amenitiy appending");
    });

  $('#btn-predict').click(function() {
    var selected = [];
    $('.checkbox input:checked').each(function() {
      // console.log($(this));
      console.log("in checkbox");
      // console.log($(this).attr('value'));
      selected.push($(this).attr('value'));
    });

    console.log(selected);

    var data = {};
    // console.log(data);

    $('form').serializeArray().forEach(function(pair) {
      data[pair.name] = pair.value;
    });

    // console.log(data);
    data['amenities'] = selected;
    data['classifier_type'] = classifier_type;
    // console.log(data);

    $('p.json').html(JSON.stringify(data));

    console.log(JSON.stringify(data));

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
        console.log(response);
        var price = Object.entries(response)[0][1];
        var similar = Object.entries(response)[1][1];
        $('p.results').text(price);
        $('p.similar').text(similar);
      }
    });
  });

  $('.non-textual').css('display', 'none');

});
 
