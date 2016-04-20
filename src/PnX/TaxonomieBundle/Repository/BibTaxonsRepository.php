<?php
namespace PnX\TaxonomieBundle\Repository;

use Doctrine\ORM\EntityRepository;


class BibTaxonsRepository extends EntityRepository
{
	public function getTaxonomieHierarchie() {
		
        $connection = $this->getEntityManager()->getConnection();
        //@TODO : refaire la requête sql pour pouvoir gérer le cas particulier des familles qui ont le même nom
        $statement = $connection->prepare("WITH tax as (
                SELECT t.*
                FROM taxonomie.taxref t
                JOIN taxonomie.bib_taxons b
                ON t.cd_nom = b.cd_nom
            ) 
            SELECT DISTINCT cd_nom, cd_taxsup, lb_nom, id_rang AS id_rang 
            FROM taxonomie.taxref WHERE id_rang IN ('KD','PH','CL','OR','FM')
            AND lb_nom IN (
                SELECT DISTINCT phylum FROM tax
                UNION
                SELECT DISTINCT regne FROM tax
                UNION
                SELECT DISTINCT classe FROM tax
                UNION
                SELECT DISTINCT ordre FROM tax
                UNION
                SELECT DISTINCT famille FROM tax
            )");
        $statement->execute();
        $results = $statement->fetchAll();
        return $results;
	}
    public function findTaxrefBibtaxons($page =0, $limit = 50 , $where, $qparameters) {
        $fieldListeQry = $this->createQueryBuilder('bibTaxons')
            ->select(['taxref.cdNom cd_nom','taxref.regne','taxref.phylum','taxref.classe','taxref.ordre','taxref.famille','taxref.cdTaxsup cd_taxsup','taxref.cdSup cd_sup','taxref.cdRef cd_ref','taxref.lbNom lb_nom','taxref.lbAuteur lb_auteur','taxref.nomComplet nom_complet','taxref.nomCompletHtml nom_complet_html','taxref.nomValide nom_valide','taxref.nomVern nom_vern','taxref.group1Inpn group1_inpn','taxref.group2Inpn group2_inpn','taxref.idRang id_rang','taxref.idStatut id_statut','taxref.idHabitat id_habitat'])
            ->join('bibTaxons.taxref', 'taxref')
            ->setFirstResult($page*$limit)
            ->setMaxResults($limit);
            
        if (count($where)>0) {
            $fieldListeQry = $fieldListeQry->where(implode(" AND ", $where))->setParameters($qparameters);
        }
        
        $results= $fieldListeQry->getQuery()->getResult();
        
        return $results;

    }
}
