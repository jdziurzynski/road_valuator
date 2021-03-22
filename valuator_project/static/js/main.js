
$(function(){
  $("#searchTab").click(function(){
    $("#confBox").hide();
    $("#searchBox").show();
  });
});

$(function(){
  $("#confTab").click(function(){
    $("#searchBox").hide();
    $("#confBox").show();
  });
});

$(function(){
  $("#start_location").change(function (){
    var location = this.value
    $.ajax({
      url: 'ajax/resolve_location/',
      data: {
        'location': location,
      },
      dataType: 'json',
      success: function (response) {
        var solved = response.location;
        document.getElementById('solved_start_address').textContent = solved
      }
    });
  });
});

$(function(){
  $("#dest_location").change(function (){
    var location = this.value
    $.ajax({
      url: 'ajax/resolve_location/',
      data: {
        'location': location,
      },
      dataType: 'json',
      success: function (response) {
        var solved = response.location;
        document.getElementById('solved_dest_address').textContent = solved
      }
    });
  });
});

$(document).on('change', '#viapointLocation', function() {
    var location = this.value
    var self = this;
    $.ajax({
      url: 'ajax/resolve_location/',
      data: {
        'location': location,
      },
      dataType: 'json',
      success: function (response) {
        var solved = response.location;
        self.nextSibling.children[0].textContent = solved
      }
    });
});
$(function(){
  $("#addViaPoint").click(function (){
    var viapoints, via_number;
    viapoints = document.getElementsByClassName("via_location_box");
    via_number = viapoints.length +1;
    var viapointsOrder = document.getElementById('viapointsOrder').style.display = 'block';
    if (viapoints.length < 1){
      var viaPointsBox = document.getElementById('viaPointsBox');
      var delBttn = document.createElement("button");
      delBttn.setAttribute('type', 'button');
      delBttn.setAttribute('id', 'delViaPoint');
      delBttn.setAttribute('class', 'btn btn-danger');
      delBttn.innerHTML = '-'
      viaPointsBox.append(delBttn);
    }
    if(viapoints.length < 8){
      var via_box = document.getElementById('viaPointsDataBox')
      var new_via_box = document.createElement("div");
      new_via_box.className = 'form-group via_location_box';
      var label = document.createElement("label");
      label.setAttribute('label', 'viapoint_'+via_number);
      label.textContent = via_number+'.';
      var input = document.createElement("input");
      input.setAttribute('type', 'text');
      input.setAttribute('id', 'viapointLocation');
      input.setAttribute('placeholder', 'Post Code or Address');
      input.className = 'form-control viapoint_input';
      var solved_box = document.createElement("div");
      solved_box.className = 'location_solved_box';
      var solved_address = document.createElement("p");
      solved_address.setAttribute('id','solved_address')
      solved_box.append(solved_address)
      new_via_box.append(label);
      new_via_box.append(input);
      new_via_box.append(solved_box);
      via_box.append(new_via_box);
    };
  });
});


$(document).on('click', '#delViaPoint', function() {
    $(".via_location_box").last().remove();
    var viapoints = document.getElementsByClassName("via_location_box");
    if(viapoints.length < 1){
      var delViaPoint = document.getElementById("delViaPoint");
      delViaPoint.remove()
      var viapointsOrder = document.getElementById('viapointsOrder').style.display = 'none';
      var optimizeViaPoints = document.getElementById('optimizeViaPoints').checked = false;
    }
});

$(function(){

  $("#calculateRoad").click(function (){
      var x, start, dest, rate, points, highways, tolls, bordercrossing, optimize
      var viapoints_dict = {}
      start = document.getElementById('start_location').value
      dest = document.getElementById('dest_location').value
      rate = document.getElementById('rate').value
      highways = document.getElementById('highways_check').checked
      tolls = document.getElementById('tolls_check').checked
      bordercrossing = document.getElementById('bordercrossing_check').checked
      optimize = document.getElementById('optimizeViaPoints').checked
      $('.viapoint_input').each(function(idx){
        var viapoint = $(this).val();
        if(viapoint){
          viapoints_dict[idx] = viapoint;
        };
        });

      $.ajax({
        url: 'ajax/proces_road/',
        data: {
          'start': start,
          'dest': dest,
          'viapoints': JSON.stringify(viapoints_dict),
          'rate': rate,
          'highways': highways,
          'tolls': tolls,
          'bordercrossing': bordercrossing,
          'optimize' : optimize
        },
        dataType: 'json',
        success: function (response) {
          solved = response.solved;
          if(solved){
            var viasBoxResult = document.getElementById('viasBoxResult');
            viasBoxResult.textContent = '';
            if(response.vias){
              var via_response = document.createElement("div");
              via_response.className = 'result_data_label';
              var via_box_response_label = document.createElement("span");
              via_box_response_label.textContent = 'Via Points in order:'
              via_response.append(via_box_response_label)
              var via_response_value_box = document.createElement("div");
              via_response_value_box.className = 'result_value'
              var via_response_value = document.createElement("p");
              via_response_value.textContent = response.vias[0];
              via_response_value_box.append(via_response_value);
              viasBoxResult.append(via_response);
              viasBoxResult.append(via_response_value_box);
              if(response.vias.length > 1){
                for (var i = 1; i<response.vias.length+1; i++){
                  var via_response = document.createElement("div");
                  via_response.className = 'result_data_label';
                  var via_box_response_label = document.createElement("span");
                  via_response.append(via_box_response_label);
                  var via_response_value_box = document.createElement("div");
                  via_response_value_box.className = 'result_value';
                  var via_response_value = document.createElement("p");
                  via_response_value.textContent = response.vias[i];
                  via_response_value_box.append(via_response_value)
                  viasBoxResult.append(via_response);
                  viasBoxResult.append(via_response_value_box);
                }
              }
            }
            document.getElementById('startResult').textContent = response.start;
            document.getElementById('destResult').textContent = response.dest;
            document.getElementById('avoidResult').textContent = response.avoid;
            document.getElementById('distanceResult').textContent = response.distance;
            document.getElementById('durationResult').textContent = response.duration;
            document.getElementById('costResult').textContent = response.cost;
            document.getElementById('resultBox').style.display = 'flex';
          };

        }
      });

    });

});
