

function init_recherche_etablissement() {
    var donnees_recherche_etablissement = [];
    $.getJSON('/gestion/liste_etablissements_json/', function(data) {
        donnees_recherche_etablissement = data;
    });

    $('.recherche_etablissement_auto').each(function() {
        var text_input = $(this);
        var hidden_input = $('#' + text_input.attr('id') + "_id");
        text_input.autocomplete({
            minLength: 3,
            source: function( request, response ) {
                    var term = request.term.toLowerCase();
                    var response_data = [];
                    for(var i = 0; i < donnees_recherche_etablissement.length; i++ ) {
                        var etablissement = donnees_recherche_etablissement[i];
                        if (etablissement.nom.toLowerCase().indexOf(term) != -1
                                || etablissement.pays__nom.toLowerCase().indexOf(term) != -1 ) {
                            response_data.push({
                                'label' : etablissement.nom + ' (' + etablissement.pays__nom + ')',
                                'value' : etablissement.id
                            });

                        }
                    }
                    response(response_data);
            },
            focus: function( event, ui ) {
                text_input.val( ui.item.label );
                return false;
            },
            select: function( event, ui ) {
                text_input.val( ui.item.label );
                hidden_input.val( ui.item ? ui.item.value : "" );
                return false;
            },
            change: function(event,ui) {
                hidden_input.val( ui.item ? ui.item.value : "" );
            }


        });
    });
}