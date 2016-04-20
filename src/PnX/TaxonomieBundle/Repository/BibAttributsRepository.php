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
}
