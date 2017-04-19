function onSubmit( form ){
      // console.log( $(form).serializeArray() );
      // var data = JSON.stringify( $(form).serializeArray() ); 
      var selected = [];
      // console.log($('div.checkbox input:checked'));
      $('div.checkbox input:checked').each(function() {
          
          selected.push($(this).attr('value'));
      });

      // console.log(selected);

   
      var data = {
          'property_type': form.property_type.value,
          'room_type': form.room_type.value,
          'person_capacity':form.person_capacity.value,
          'bedrooms':form.bedrooms.value,
          'beds':form.bedrooms.value,
          'bathrooms':form.bathrooms.value,
          'amenities':selected,
          'address':form.amenities.value,
          'house_rules':form.amenities.value,
          'description': form.description.value,
          'classifier_type':form.classifier_type.value
      };
      var dataString =  JSON.stringify(data);
    // console.log(dataString);

      $.ajax({
        url:'/host/predict',
        type: 'post',
        data: dataString,
        contentType:"application/json",
        success: function(response){
                        console.log("success");
                        // Hide the form
                        $("form")[0].style.display = "none";
                        // Displayed the submitted info
                        $("p.json")[0].innerHTML = dataString;
                        
                        // Display result
                        var price = Object.entries(response)[0][1];
                        console.log(price)
                        var similar = Object.entries(response)[1][1];
                        console.log(similar)
                        $("p.results")[0].innerHTML = price;
                        $("p.similar")[0].innerHTML = similar;
                        
        },

        error: function () { console.log("alert"); },
        dataType: 'json'
      });

      return false; //don't submit
}



