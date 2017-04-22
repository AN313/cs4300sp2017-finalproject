$(document).ready(function() {
  $('#row-input').show();
  $('#row-prediction').hide();

  $("[name='my-checkbox']").bootstrapSwitch();

  $("[name='my-checkbox']").on('switchChange.bootstrapSwitch', function(e, state) {
    //console.log("what");
    if (state) {
      $('.non-textual').css('display', 'none');
    } else {
      $('.non-textual').css('display', 'block');
    }
  });

   // add amenities dynamically
  var amenities = [
    'Pets in the house',
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
    'Hair dryer'
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
    $('div.checkbox input:checked').each(function() {
      selected.push($(this).attr('value'));
    });

    var data = {};
    $('form').serializeArray().forEach(function(pair) {
      data[pair.name] = pair.value;
    });

    $('p.json').html(JSON.stringify(data));

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
        var price = Object.entries(response)[0][1];
        var similar = Object.entries(response)[1][1];
        $('p.results').text(price);
        $('p.similar').text(similar);
      }
    });
  });

  $('.non-textual').css('display', 'none');

});
 
