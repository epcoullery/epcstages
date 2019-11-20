django.jQuery(document).ready(function() {
  django.jQuery('#id_corporation, .field-corporation select').change(function(ev) {
    // Fill contact select
    // Either in availability admin, or in stages admin with availability inlines
    if (this.id == 'id_period') return;
    if (this.id == 'id_corporation') var sel = django.jQuery('#id_contact');
    else var sel = django.jQuery(this).closest('fieldset').find('.field-contact select');
    var id_corp = django.jQuery("option:selected", this).val();
    django.jQuery.getJSON('/corporation/' + id_corp + '/contacts/', function(data) {
        if (data.length && data[0].corporation_id == id_corp) return
        sel.html('<option value="">-------</option>');
        django.jQuery.each(data, function(key, contact) {
            var item = contact.first_name + ' ' + contact.last_name;
            if (contact.role.length) item += ' (' + contact.role + ')';
            sel.append(django.jQuery("<option />").val(contact.id).text(item));
        });
        if (data.length == 1) sel.val(data[0].id);
    });
  });
});
