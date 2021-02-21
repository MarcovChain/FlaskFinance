// hist.js
const updatePlot = (data) => {
    $.ajax({
        url: 'graph',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        data: {
          'bins': data.from
        },
        dataType: 'json',
        success: function(data){
          Plotly.newPlot('histogram', data)
        }
      });
  }
  
  $('.js-range-slider').ionRangeSlider({
      type: 'single',
      skin: 'big',
      min: 1,
      max: 50,
      step: 1,
      from: 30,
      grid: true,
      onStart: updatePlot,
      onFinish: updatePlot
  });