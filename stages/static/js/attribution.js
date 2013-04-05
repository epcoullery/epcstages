function update_periods(section_id) {
  $.getJSON('/section/' + section_id + '/periods/', function(data) {
    var sel = $('#period_select');
    sel.append($("<option />").val('').text('-------'));
    if (data.length > 0) {
      $.each(data, function() {
        sel.append($("<option />").val(this.id).text(this.dates + ' ' + this.title));
      })
    }
    if ($.cookie('periode') != 'undefined')
        sel.val($.cookie('periode'));

    var periode_val = sel.val();
    update_students(periode_val);
    update_corporations(periode_val);
    update_trainings(periode_val);
  });
}

function update_students(period_id) {
  $('#student_select').empty();
  $('#student_filter').empty();
  $('#student_detail').html('').removeClass("filled");
  current_student = null;
  $('input#valid_training').hide();
  if (period_id == '') return;
  $.getJSON('/period/' + period_id + '/students/', function(data) {
    var sel = $('#student_select');
    var classes = [];
    var options = [];
    $('#student_filter').append($("<option />").val('').text('Toutes les classes'));
    $.each(data, function() {
      if (this.training_id == null) {
        options.push(this);
        sel.append($("<option />").val(this.id).text(this.name + ' (' + this.klass + ')'));
      }
      if ($.inArray(this.klass, classes) < 0) {
        classes.push(this.klass);
        $('#student_filter').append($("<option />").val(this.klass).text(this.klass));
      }
    });
    // Keep options as data to enable filtering
    sel.data('options', options);
    $('div#student_total').html(options.length + " étudiant-e-s").data('num', options.length);
  });
}

function update_corporations(period_id) {
  $('#corp_select').empty();
  $('#corp_detail').html('').removeClass("filled");
  current_avail = null;
  $('#contact_select').find('option:gt(0)').remove();
  $('input#valid_training').hide();
  if (period_id == '') return;
  $.getJSON('/period/' + period_id + '/corporations/', function(data) {
    var sel = $('#corp_select');
    var domains = [];
    var options = [];
    $('#corp_filter').empty().append($("<option />").val('').text('Tous les domaines'));
    // data contains availabilities (id is availability not corporation)
    $.each(data, function() {
      if (this.free) {
        options.push(this);
        sel.append($("<option />").val(this.id).text(this.corp_name).data('id_corp', this.id_corp));
      }
      if ($.inArray(this.domain, domains) < 0) {
        domains.push(this.domain);
        $('#corp_filter').append($("<option />").val(this.domain).text(this.domain));
      }
    });
    sel.data('options', options);
    $('div#corp_total').html(options.length + " disponibilités").data('num', options.length);
  });
}

function update_trainings(period_id) {
  function set_export_visibility() {
      if ($('ul#training_list').children().length > 0)
        $('input#export').show();
      else $('input#export').hide();
  }

  if (period_id == '') $('ul#training_list').html('');
  else $('ul#training_list').load('/training/by_period/' + period_id + '/', function() {
      $('img.delete_training').click(function() {
        if (!confirm("Voulez-vous vraiment supprimer ce stage ?")) return;
        var li = $(this).parents('li');
        $.post('/training/del/',
          {pk: li.attr('id').split('_')[1],
           csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val()}, function(data) {
            li.remove();
            // dispatch student and corp in their listings
            update_students($('#period_select').val());
            update_corporations($('#period_select').val());
            set_export_visibility();
            // Decrement referent number
            var referent = $('#referent_select option[value="' + data.ref_id + '"]')
            var parsed = referent.text().match(/(.*)\((\d+)\)/);
            referent.text(parsed[1] +' (' + (parseInt(parsed[2]) - 1) + ')');
        });
      });
      $('a.edit_training').click(function(ev) {
        ev.preventDefault();
        showAddAnotherPopup(this);
      });
      set_export_visibility();
  });
}

$(document).ready(function() {
  $('#section_select').change(function(ev) {
    // Update period list when section is modified
    $('#period_select').empty();
    update_periods($(this).val());
    $.cookie('section', $(this).val(), { expires: 7 });
    $.removeCookie('periode');
  });

  $('#period_select').change(function(ev) {
    // Update student/corporation list when period is modified
    update_students($(this).val());
    update_corporations($(this).val());
    update_trainings($(this).val());
    $.cookie('periode', $(this).val(), { expires: 7 });
  });

  $('#student_filter').change(function(ev) {
    var sel = $('#student_select');
    var options = sel.data('options');
    var filter_val = $(this).val();
    sel.empty();
    $.each(options, function(i) {
        var option = options[i];
        if (option.klass == filter_val || filter_val == '') {
          sel.append($("<option />").val(option.id).text(option.name + ' (' + option.klass + ')'));
        }
    });
  });

  $('#student_select').change(function(ev) {
    $('#student_detail').load('/student/' + $(this).val() + '/summary/', function() {
        $('div#previous_stages_head').toggle(function() {
            $('ul#previous_stages_list').toggle();
            $(this).find('img').attr('src', static_url + 'img/open.png');
        }, function() {
            $('ul#previous_stages_list').toggle();
            $(this).find('img').attr('src', static_url + 'img/closed.png');
        });
    }).addClass("filled");
    current_student = $(this).val();
    if (current_avail !== null) $('input#valid_training').show();
  });

  $('#corp_filter').change(function(ev) {
    var sel = $('#corp_select');
    var options = sel.data('options');
    var filter_val = $(this).val();
    sel.empty();
    $.each(options, function(i) {
        var option = options[i];
        if (option.domain == filter_val || filter_val == '') {
          sel.append($("<option />").val(option.id).text(option.corp_name));
        }
    });
  });

  $('#corp_select').change(function(ev) {
    $('#corp_detail').load('/availability/' + $(this).val() + '/summary/').addClass("filled");
    current_avail = $(this).val();
    if (current_student !== null) $('input#valid_training').show();
    // Fill contact select
    var sel = $('#contact_select');
    sel.html('<option value="">-------</option>');
    var id_corp = $("option:selected", this).data('id_corp');
    $.getJSON('/corporation/' + id_corp + '/contacts/', function(data) {
        $.each(data, function(key, contact) {
            var item = contact.first_name + ' ' + contact.last_name;
            if (contact.role.length) item += ' (' + contact.role + ')';
            sel.append($("<option />").val(contact.id).text(item));
        });
        if (data.length == 1) sel.val(data[0].id);
    });
  });

  $('#valid_training').click(function() {
    $.post('/training/new/', {
            student: current_student, avail: current_avail,
            referent: $('#referent_select').val(),
            contact: $('#contact_select').val(),
            csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val()},
        function(data) {
          if (data != 'OK') {
            alert(data);
            return;
          }
          // Clear selected student/corp
          $('option:selected', '#student_select').remove();
          var prev_num = $('div#student_total').data('num');
          $('div#student_total').html((prev_num - 1) + " étudiant-e-s").data('num', prev_num - 1);
          $('#student_detail').html('').removeClass("filled");
          $('option:selected', '#corp_select').remove();
          prev_num = $('div#corp_total').data('num');
          $('div#corp_total').html((prev_num - 1) + " disponibilités").data('num', prev_num - 1);
          $('#corp_detail').html('').removeClass("filled");
          current_student = null;
          current_avail = null;
          $('input#valid_training').hide();

          // Update referent select
          var parsed = $('#referent_select option:selected').text().match(/(.*)\((\d+)\)/);
          if (parsed) {
            $('#referent_select option:selected').text(parsed[1] +' (' + (parseInt(parsed[2]) + 1) + ')');
            $('#referent_select').val('');
          }

          update_trainings($('#period_select').val());
        }
    );
  });

  $('input#export').click(function(ev) {
    ev.preventDefault();
    $('form#list_export').find('input#filter').val($('#period_select').val());
    $('form#list_export').submit();
  });

  if ($.cookie('section') != 'undefined')
    $('#section_select').val($.cookie('section'));
  update_periods($('#section_select').val());
});

var current_student = null;
var current_avail = null;
