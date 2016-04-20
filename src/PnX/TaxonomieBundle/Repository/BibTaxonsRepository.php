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
            ->select(['taxref.cdNom','taxref.regne','taxref.phylum','taxref.classe','taxref.ordre','taxref.famille','taxref.cdTaxsup','taxref.cdSup','taxref.cdRef','taxref.lbNom','taxref.lbAuteur','taxref.nomComplet','taxref.nomCompletHtml','taxref.nomValide','taxref.nomVern','taxref.group1Inpn','taxref.group2Inpn','taxref.idRang','taxref.idStatut','taxref.idHabitat'])
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
