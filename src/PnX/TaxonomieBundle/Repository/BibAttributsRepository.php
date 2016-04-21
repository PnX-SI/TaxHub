<?php
namespace PnX\TaxonomieBundle\Repository;

use Doctrine\ORM\EntityRepository;


class BibAttributsRepository extends EntityRepository {
    
    public function findAllByFilter($where, $qparameters) {
        $fieldListeQry = $this->createQueryBuilder('BibAttributs');   
        if (count($where)>0) {
            $fieldListeQry = $fieldListeQry->where(implode(" AND ", $where))->setParameters($qparameters);
        }
        
        $results= $fieldListeQry->getQuery()->getResult();
        
        return $results;
    }
    public function findAttributsByOneTaxon($id) {
        $connection = $this->getEntityManager()->getConnection();
        $statement = $connection->prepare("
            SELECT a.*, cta.valeur_attribut
            FROM taxonomie.cor_taxon_attribut cta 
            JOIN taxonomie.bib_attributs a ON a.id_attribut = cta.id_attribut
            WHERE cta.id_taxon = ".$id);
        $statement->execute();
        $results = $statement->fetchAll();
        // $results = (object)$statement->fetchAll();
        return $results;
    }
}
