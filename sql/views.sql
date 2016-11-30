DROP VIEW IF EXISTS invitations;

CREATE ALGORITHM = UNDEFINED
  SQL SECURITY DEFINER VIEW `invitations` AS
  SELECT
    `e`.`nom`         AS `etablissement_nom`,
    `e`.`id`          AS `etablissement_id`,
    `e`.`region_id`   AS `etablissement_region_id`,
    `i`.`jeton`       AS `jeton`,
    `env`.`id`        AS `enveloppe_id`,
    `env`.`modele_id` AS `modele_id`,
    `p`.`sud`         AS `sud`,
    `e`.`statut`      AS `statut`
  FROM ((((`mailing_enveloppe` `env`
    JOIN `inscription_invitationenveloppe` `ie`
      ON ((`env`.`id` = `ie`.`enveloppe_id`))) JOIN `inscription_invitation` `i`
      ON ((`i`.`id` = `ie`.`invitation_id`))) JOIN `reference_etablissement` `e`
      ON ((`e`.`id` = `i`.`etablissement_id`))) JOIN `reference_pays` `p`
      ON ((`p`.`id` = `e`.`pays_id`)))
