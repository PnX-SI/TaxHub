<?php
namespace PnX\TaxonomieBundle\Repository;

use Doctrine\ORM\EntityRepository;


class CorTaxonAttributRepository extends EntityRepository {
  
  
	public function findTaxonsList($id) {
		
        $connection = $this->getEntityManager()->getConnection();
        //@TODO : refaire la requête sql pour pouvoir gérer le cas particulier des familles qui ont le même nom
        $statement = $connection->prepare("SELECT b.*, c.valeur_attribut 
            FROM taxonomie.bib_taxons b
            JOIN (SELECT * FROM  taxonomie.cor_taxon_attribut WHERE id_attribut = ".$id.") c
            ON c.id_taxon = b.id_taxon");
        $statement->execute();
        $results = $statement->fetchAll();
        return $results;
	}
}
