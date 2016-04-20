<?php
namespace PnX\TaxonomieBundle\Repository;

use Doctrine\ORM\EntityRepository;


class CorTaxonAttributRepository extends EntityRepository {
  
  
	public function findTaxonsList($id, $value) {
		
        $connection = $this->getEntityManager()->getConnection();
        //@TODO : refaire la requête sql pour pouvoir gérer le cas particulier des familles qui ont le même nom
        $where = "WHERE id_attribut = ".$id;
        if($value != null){
            $where .= " AND valeur_attribut = '".$value."'";
        }
        $statement = $connection->prepare("SELECT b.*, a.nom_attribut, c.valeur_attribut 
            FROM taxonomie.bib_taxons b
            JOIN (SELECT * FROM  taxonomie.cor_taxon_attribut ".$where.") c ON c.id_taxon = b.id_taxon
            JOIN taxonomie.bib_attributs a ON a.id_attribut = c.id_attribut
            ");
        $statement->execute();
        $results = $statement->fetchAll();
        return $results;
	}
}
