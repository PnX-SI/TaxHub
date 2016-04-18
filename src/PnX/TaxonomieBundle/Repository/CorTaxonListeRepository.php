<?php
namespace PnX\TaxonomieBundle\Repository;

use Doctrine\ORM\EntityRepository;


class CorTaxonListeRepository extends EntityRepository {
  
  
	public function findTaxonsList($id) {
		
        $connection = $this->getEntityManager()->getConnection();
        //@TODO : refaire la requête sql pour pouvoir gérer le cas particulier des familles qui ont le même nom
        $statement = $connection->prepare("SELECT b.* 
            FROM taxonomie.bib_taxons b
            JOIN (SELECT * FROM  taxonomie.cor_taxon_liste WHERE id_liste = ".$id.") c
            ON c.id_taxon = b.id_taxon");
        $statement->execute();
        $results = $statement->fetchAll();
        return $results;
	}
}
