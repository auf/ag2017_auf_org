insert into reference_pays (id, code, nom, sud)
select id, code, nom, IF(nord_sud="Sud", True, False) from datamaster.ref_pays;
insert into reference_region (id, code, nom)
select id, code, nom from datamaster.ref_region;
insert into reference_etablissement(id, nom, adresse, code_postal, ville,
    telephone, fax, responsable_genre, responsable_nom, responsable_prenom,
    responsable_fonction, responsable_courriel, statut, qualite, pays_id,
                                    region_id,
    membre)
select e.id, e.nom, adresse, code_postal, ville, telephone, fax,
  responsable_genre, responsable_nom, responsable_prenom,
  responsable_fonction, responsable_courriel, statut, qualite, p.id, r.id,
  membre
from (datamaster.ref_etablissement e
  left join datamaster.ref_pays p on e.pays = p.code)
  left join datamaster.ref_region r on e.region = r.id;
