INSERT INTO reference_pays (id, code, nom, sud)
  SELECT
    id,
    code,
    nom,
    IF(nord_sud = 'Sud', TRUE, FALSE)
  FROM datamaster.ref_pays drp
ON DUPLICATE KEY UPDATE
  code=drp.code, nom=drp.nom, sud=(IF (drp.nord_sud='Sud', TRUE, FALSE ));

INSERT INTO reference_region (id, code, nom)
  SELECT
    id,
    code,
    nom
  FROM datamaster.ref_region drr
ON DUPLICATE KEY UPDATE
  code = drr.code, nom = drr.nom;

INSERT INTO reference_etablissement (id, nom, adresse, code_postal, ville,
                                     telephone, fax, responsable_genre, responsable_nom, responsable_prenom,
                                     responsable_fonction, responsable_courriel, statut, qualite, pays_id,
                                     region_id,
                                     membre)
  SELECT
    e.id,
    e.nom,
    e.adresse,
    e.code_postal,
    e.ville,
    e.telephone,
    e.fax,
    e.responsable_genre,
    e.responsable_nom,
    e.responsable_prenom,
    e.responsable_fonction,
    e.responsable_courriel,
    e.statut,
    e.qualite,
    p.id,
    r.id,
    e.membre
  FROM (datamaster.ref_etablissement e
    LEFT JOIN datamaster.ref_pays p ON e.pays = p.code)
    LEFT JOIN datamaster.ref_region r ON e.region = r.id
ON DUPLICATE KEY UPDATE
  nom                  = e.nom, adresse = e.adresse,
  code_postal          = e.code_postal, ville = e.ville,
  telephone            = e.telephone, fax = e.fax,
  responsable_genre    = e.responsable_genre,
  responsable_nom      = e.responsable_nom,
  responsable_prenom   = e.responsable_prenom,
  responsable_fonction = e.responsable_fonction,
  responsable_courriel = e.responsable_courriel, statut = e.statut,
  qualite              = e.qualite, pays_id = p.id, region_id = r.id,
  membre               = e.membre;


INSERT INTO reference_implantation (id, nom, nom_court, region_id)
  SELECT
    id,
    nom,
    nom_court,
    region
  FROM datamaster.ref_implantation dri
ON DUPLICATE KEY UPDATE nom = dri.nom, nom_court = dri.nom_court,
region_id = dri.region;
